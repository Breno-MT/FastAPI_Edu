from sqlalchemy import select

from fast_zero.models import User

def test_create_user(session):
    user = User(username="brenindostest",
                password="top10senhasdahistoria",
                email="brenin@gmail.com",
    )
    session.add(user)
    session.commit()
    result = session.scalar(select(User).where(User.email == "brenin@gmail.com"))
    assert result.username == "brenindostest"
