import pytest

from app import create_app, db
from .test_config import test_config
from app.models import User

@pytest.fixture(scope='module')
def test_client():
    test_app = create_app(test_config)

    with test_app.test_client() as client:
        with test_app.app_context():
            yield client

@pytest.fixture(scope='module')
def init_database():
    db.drop_all()
    db.create_all()

    user1 = User('user1', test_config.DEFAULT_BALANCE)
    user2 = User('user2', test_config.DEFAULT_BALANCE)
    user3 = User('user3', test_config.DEFAULT_BALANCE)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)

    db.session.commit()

    yield

    db.session.flush()
