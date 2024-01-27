import sqlalchemy
from sqlalchemy.orm import sessionmaker
from providers.vk_access_creds import file_path  # eugiv only
from postgres_db.models import create_tables
from postgres_db import models as m
from postgres_db.aws_postgres_conn import DBConnector  # eugiv only

# DSN = "postgresql://postgres:touching@localhost:5432/VKinder"

create_connection = DBConnector(
    file_path, "localhost", 5432, "ubuntu", 22, "postgres", "vkinder"
)  # eugiv only
tunnel = create_connection.connection()  # eugiv only


# DSN = "postgresql://postgres:********@localhost:5432/db_vkinder"  # prekinii only

DSN = (
    f"postgresql://{create_connection.database_user}:{create_connection.postgres_password}@localhost:"
    f"{tunnel.local_bind_port}/{create_connection.database}"
)  # eugiv only


engine = sqlalchemy.create_engine(DSN)

create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()


def add_user(vk_user_id: int, sex: int, age: int, city: str):
    with Session() as session:
        user_find = session.query(m.User.vk_user_id).all()
        if vk_user_id not in [user[0] for user in user_find]:
            user = m.User(
                vk_user_id=vk_user_id,
                sex=sex,
                age=age,
                city=city,
            )
            session.add(user)
            session.commit()


def add_offer(first_name: str, last_name: str, profile_link: str, user_id: int):
    with Session() as session:
        offer = m.Offer(
            first_name=first_name,
            last_name=last_name,
            profile_link=profile_link,
            user_id=user_id,
        )
        session.add(offer)
        session.commit()


def add_interest(interest, vk_user_id=0, vk_offer_id=0):
    with Session() as session:
        interest_find = session.query(m.Interest.interest).filter(
            m.Interest.interest == interest
        )

        if interest not in interest_find:
            interest_add = m.Interest(interest=interest)
            session.add(interest_add)

        interest_id_find = session.query(m.Interest.interest_id).filter(
            m.Interest.interest == interest
        )

        user_find = (
            session.query(m.InterestPerson.vk_user_id)
            .filter(m.InterestPerson.interest_id == interest_id_find)
            .filter(m.InterestPerson.vk_user_id == vk_user_id)
            .all()
        )
        offer_find = (
            session.query(m.InterestPerson.vk_offer_id)
            .filter(m.InterestPerson.interest_id == interest_id_find)
            .filter(m.InterestPerson.vk_offer_id == vk_offer_id)
            .all()
        )
        if vk_user_id != 0 and vk_user_id not in [user[0] for user in user_find]:
            interest_person_add = m.InterestPerson(
                vk_user_id=vk_user_id, interest_id=interest_id_find
            )
            session.add(interest_person_add)
        if vk_offer_id != 0 and vk_offer_id not in [offer[0] for offer in offer_find]:
            interest_person_add = m.InterestPerson(
                vk_offer_id=vk_offer_id, interest_id=interest_id_find
            )
            session.add(interest_person_add)
        session.commit()


def get_offer_list(user_hunter):
    with Session() as session:
        offer_list = []
        show_offer_list = (
            session.query(
                m.Offer.vk_offer_id,
                m.Offer.first_name,
                m.Offer.last_name,
                m.Offer.profile_link,
            )
            .join(m.UserOffer, m.UserOffer.vk_offer_id == m.Offer.vk_offer_id)
            .join(m.User, m.User.vk_user_id == m.UserOffer.vk_user_id)
            .filter(m.User.vk_user_id == user_hunter)
            .filter(m.UserOffer.black_list == 0)
            .all()
        )
        for x in show_offer_list:
            offer_list.append(f"{x.first_name} | {x.last_name} | {x.profile_link}\n")
    return offer_list


def show_offer(person_id):  # Показать найденыша
    with Session() as session:
        found_match = False

        while not found_match:
            offer = session.query(
                m.Offer.vk_offer_id,
                m.Offer.first_name,
                m.Offer.last_name,
                m.Offer.profile_link,
                m.Offer.user_id,
            ).filter(m.Offer.vk_offer_id == person_id)

            for x in offer:
                person = f"{x.first_name} | {x.last_name} | {x.profile_link}"
                user_id = x.user_id
                found_match = True

        return {"person": person, "user_id": user_id}


def add_user_offer(add_offer_id, user_hunter, friend_or_foe):
    with Session() as session:
        add_offer_id = session.query(
            m.Offer.vk_offer_id,
        ).filter(m.Offer.vk_offer_id == add_offer_id)
        if friend_or_foe == "friend":
            black_list = 0
            favorite_list = 1
        else:
            black_list = 1
            favorite_list = 0

        user_offer = m.UserOffer(
            vk_user_id=user_hunter,
            vk_offer_id=add_offer_id,
            black_list=black_list,
            favorite_list=favorite_list,
        )
    session.add(user_offer)
    session.commit()


session.close()
