# Importa todos os modelos aqui para que o Alembic possa detectá-los
from app.db.base_class import Base  # noqa
from app.models.diagnostic import Diagnostic  # noqa
from app.models.report import Report  # noqa
from app.models.system_info import SystemInfo  # noqa