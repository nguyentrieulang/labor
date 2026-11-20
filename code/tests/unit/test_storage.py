import pytest
import sqlalchemy as sa

from labour.adapters.storage.db import make_engine, migrate
from labour.adapters.storage.models import Base


def _seed(c):
    c.exec_driver_sql("INSERT INTO users(id,tg_user_id,display_name,is_admin,can_create_group,active,created_at) "
                      "VALUES (1,111,'A',1,1,1,'t'),(2,222,'B',0,0,1,'t')")
    c.exec_driver_sql("INSERT INTO bots(id,username,token_env,created_at) VALUES (1,'b1','BOT1_TOKEN','t')")
    c.exec_driver_sql("INSERT INTO groups(id,tg_chat_id,title,owner_user_id,security_level,workspace_path,"
                      "system_bot_id,gemini_enabled,status,created_at,updated_at) "
                      "VALUES (1,-100,'g',1,'noi_bo','w',1,0,'active','t','t')")


def _role(c, status):
    c.exec_driver_sql("INSERT INTO role_assignments(group_id,bot_id,role_name,instructions,source_text,provider,"
                      f"is_reviewer,status,version,created_at,updated_at) VALUES (1,1,'r','i','s','claude',0,'{status}',1,'t','t')")


@pytest.fixture(params=["create_all", "alembic"])
def engine(request, tmp_path):
    eng = make_engine(tmp_path / "t.db")
    if request.param == "alembic":
        migrate(eng)
    else:
        Base.metadata.create_all(eng)
    with eng.begin() as c:
        _seed(c)
    return eng


def test_migration_matches_models(tmp_path):
    eng = make_engine(tmp_path / "t.db")
    migrate(eng)
    names = set(sa.inspect(eng).get_table_names()) - {"alembic_version"}
    assert names == set(Base.metadata.tables)
    assert len(names) == 16


def test_pragmas(tmp_path):
    eng = make_engine(tmp_path / "t.db")
    with eng.connect() as c:
        assert c.exec_driver_sql("PRAGMA journal_mode").scalar() == "wal"
        assert c.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1
        assert c.exec_driver_sql("PRAGMA busy_timeout").scalar() == 5000


def test_only_one_owner_per_group(engine):
    with engine.begin() as c:
        c.exec_driver_sql("INSERT INTO group_members(group_id,user_id,role,joined_at) VALUES (1,1,'chu','t')")
    with pytest.raises(sa.exc.IntegrityError), engine.begin() as c:
        c.exec_driver_sql("INSERT INTO group_members(group_id,user_id,role,joined_at) VALUES (1,2,'chu','t')")


def test_one_active_role_per_bot_per_group(engine):
    with engine.begin() as c:
        _role(c, "hieu_luc")
        _role(c, "thay_the")
    with pytest.raises(sa.exc.IntegrityError), engine.begin() as c:
        _role(c, "hieu_luc")


def test_security_level_check(engine):
    with pytest.raises(sa.exc.IntegrityError), engine.begin() as c:
        c.exec_driver_sql("UPDATE groups SET security_level='mo' WHERE id=1")


def test_foreign_key_enforced(engine):
    with pytest.raises(sa.exc.IntegrityError), engine.begin() as c:
        c.exec_driver_sql("INSERT INTO group_members(group_id,user_id,role,joined_at) VALUES (1,99,'thanh_vien','t')")
