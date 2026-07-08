from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.orm import Session

from checkin.service import checkin_member
from core.config import settings
from models.checkin import CheckIn, ResultadoCheckin
from models.membership import Membership
from models.checkin_device_lock import CheckinDeviceLock


class TestCheckinExitoso:
    def test_checkin_exitoso_descuenta_visita(self, db: Session, sample_data):
        result = checkin_member(sample_data["user"].cedula, "device-1", db)

        assert result["resultado"] == "exitoso"
        assert result["nombre"] == "Juan Perez"
        assert result["visitas_restantes"] == 4

        membership = db.query(Membership).filter(Membership.id == sample_data["membership"].id).first()
        assert membership.visitas_restantes == 4

    def test_checkin_exitoso_persiste_checkin(self, db: Session, sample_data):
        result = checkin_member(sample_data["user"].cedula, "device-1", db)

        assert result["resultado"] == "exitoso"
        checkin = db.query(CheckIn).filter(CheckIn.usuario_id == sample_data["user"].id).first()
        assert checkin is not None
        assert checkin.resultado == ResultadoCheckin.exitoso
        assert checkin.fecha == datetime.now(ZoneInfo(settings.timezone)).date()


class TestDobleCheckinMismoDia:
    def test_segundo_checkin_mismo_dia_es_denegado(self, db: Session, sample_data):
        checkin_member(sample_data["user"].cedula, "device-1", db)
        result = checkin_member(sample_data["user"].cedula, "device-1", db)

        assert result["resultado"] == "denegado"
        assert result["razon"] == "YA_INGRESO_HOY"

    def test_doble_checkin_no_descuenta_visita_extra(self, db: Session, sample_data):
        checkin_member(sample_data["user"].cedula, "device-1", db)
        checkin_member(sample_data["user"].cedula, "device-1", db)

        membership = db.query(Membership).filter(Membership.id == sample_data["membership"].id).first()
        assert membership.visitas_restantes == 4


class TestAccesoDenegado:
    def test_cedula_desconocida_crea_cortesia(self, db: Session, sample_data):
        result = checkin_member("99999999", "device-1", db)

        assert result["resultado"] == "exitoso"
        assert result["cortesia"] is True

    def test_segunda_cortesia_misma_cedula(self, db: Session, sample_data):
        checkin_member("88888888", "device-2", db)
        result = checkin_member("88888888", "device-2", db)

        assert result["resultado"] == "denegado"
        assert result["razon"] == "CORTESIA_YA_UTILIZADA"

    def test_membresia_vencida(self, db: Session, sample_data):
        membership = sample_data["membership"]
        membership.fecha_vencimiento = datetime.now(ZoneInfo(settings.timezone)).date().replace(year=2020)
        db.commit()

        result = checkin_member(sample_data["user"].cedula, "device-1", db)

        assert result["resultado"] == "denegado"
        assert result["razon"] == "SIN_MEMBRESIA_ACTIVA"

    def test_sin_visitas(self, db: Session, sample_data):
        membership = sample_data["membership"]
        membership.visitas_restantes = 0
        db.commit()

        result = checkin_member(sample_data["user"].cedula, "device-1", db)

        assert result["resultado"] == "denegado"
        assert result["razon"] == "SIN_MEMBRESIA_ACTIVA"

    def test_denegado_no_toca_saldos(self, db: Session, sample_data):
        original_visitas = sample_data["membership"].visitas_restantes
        checkin_member("99999999", "device-1", db)

        membership = db.query(Membership).filter(Membership.id == sample_data["membership"].id).first()
        assert membership.visitas_restantes == original_visitas


class TestDeviceLock:
    def test_tres_fallidos_bloquea(self, db: Session, sample_data):
        membership = sample_data["membership"]
        membership.visitas_restantes = 0
        db.commit()

        for i in range(3):
            checkin_member(sample_data["user"].cedula, "device-lock-1", db)

        result = checkin_member(sample_data["user"].cedula, "device-lock-1", db)
        assert result["resultado"] == "denegado"
        assert result["razon"] == "DISPOSITIVO_BLOQUEADO"

    def test_exito_resetea_contador(self, db: Session, sample_data):
        membership = sample_data["membership"]
        membership.visitas_restantes = 0
        db.commit()

        for i in range(2):
            checkin_member(sample_data["user"].cedula, "device-reset-1", db)

        membership.visitas_restantes = 5
        db.commit()
        checkin_member(sample_data["user"].cedula, "device-reset-1", db)

        lock = db.query(CheckinDeviceLock).filter(CheckinDeviceLock.device_id == "device-reset-1").first()
        assert lock is not None
        assert lock.intentos_fallidos == 0
        assert lock.bloqueado_hasta is None
