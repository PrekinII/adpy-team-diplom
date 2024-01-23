import sys
import sqlalchemy
from pprint import pprint
from sqlalchemy.orm import sessionmaker
from VK_access.vk_access_creds import file_path  # eugiv only
from VKinder_DB.models import create_tables
from VKinder_DB import models as m
from VKinder_DB.aws_postgres_conn import DBConnector  # eugiv only

# DSN = "postgresql://postgres:touching@localhost:5432/VKinder"

create_connection = DBConnector(
    file_path, "localhost", 5432, "ubuntu", 22, "postgres", "vkinder"
)  # eugiv only
tunnel = create_connection.connection()  # eugiv only


#DSN = "postgresql://postgres:*******@localhost:5432/db_vkinder"  # prekinii only

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
        print(user_find)
        if vk_user_id not in [user[0] for user in user_find]:
            user = m.User(
                vk_user_id=vk_user_id,
                sex=sex,
                age=age,
                city=city,
            )
            session.add(user)
            session.commit()


def add_offer(vk_user_id, first_name, last_name, profile_link):
    with Session() as session:
        offer = m.Offer(
            first_name=first_name,
            last_name=last_name,
            profile_link=profile_link,
        )
        session.add(offer)
        session.flush()

        vk_offer_id = offer.vk_offer_id

        user_offer_find = (
            session.query(m.UserOffer.user_offer_id)
            .filter(m.UserOffer.vk_user_id == vk_user_id)
            .filter(m.UserOffer.vk_offer_id == vk_offer_id)
            .all()
    )

        if len(user_offer_find) == 0:
            user_offer = m.UserOffer(
                vk_user_id=vk_user_id,
                vk_offer_id=vk_offer_id,
                black_list=0,
                favorite_list=0,
            )
            session.add(user_offer)
            session.commit()


def add_black_list(vk_user_id, vk_offer_id):
    with Session() as session:
        session.query(m.UserOffer).filter(
            m.UserOffer.vk_offer_id == vk_offer_id
        ).filter(m.UserOffer.vk_user_id == vk_user_id).filter(
            m.UserOffer.black_list == 0
        ).update(
            {"black_list": 1}
        )
        session.commit()


def add_favorite(vk_user_id, vk_offer_id):
    with Session() as session:
        session.query(m.UserOffer).filter(
            m.UserOffer.vk_offer_id == vk_offer_id
        ).filter(m.UserOffer.vk_user_id == vk_user_id).filter(
            m.UserOffer.black_list == 0
        ).update(
            {"favorite_list": 1}
        )
        session.commit()


def add_photo(vk_offer_id, photo_url):
    with Session() as session:
        for url in photo_url:
            photo = m.Photo(vk_offer_id=vk_offer_id, photo_url=url)
            session.add(photo)
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


def get_offer_info(vk_user_id, offer):
    offer_list = []
    with Session() as session:
        user_interests = (
            session.query(m.Interest.interest)
            .join(
                m.InterestPerson, m.InterestPerson.interest_id == m.Interest.interest_id
            )
            .filter(m.InterestPerson.vk_user_id == vk_user_id)
            .all()
        )
        for note in offer:
            offer_list.append([])
            for el in note:
                offer_list[-1].append(el)
            photo = (
                session.query(m.Photo.photo_url)
                .filter(m.Photo.vk_offer_id == note[0])
                .all()
            )
            offer_list[-1].append([url[0] for url in photo])
            offer_interests = (
                session.query(m.Interest.interest)
                .join(
                    m.InterestPerson,
                    m.InterestPerson.interest_id == m.Interest.interest_id,
                )
                .filter(m.InterestPerson.vk_offer_id == note[0])
                .all()
            )
            interest_list = []
            for interest in [inter_user[0] for inter_user in user_interests]:
                if interest in [inter_offer[0] for inter_offer in offer_interests]:
                    interest_list.append(interest)
            offer_list[-1].append(interest_list)
    return offer_list


def get_offer(vk_user_id):
    with Session() as session:
        offer = (
            session.query(
                m.Offer.vk_offer_id,
                m.Offer.first_name,
                m.Offer.last_name,
                m.Offer.profile_link,
            )
            .join(m.UserOffer, m.UserOffer.vk_offer_id == m.Offer.vk_offer_id)
            .join(m.User, m.User.vk_user_id == m.UserOffer.vk_user_id)
            .filter(m.User.vk_user_id == vk_user_id)
            .filter(m.UserOffer.black_list == 0)
            .all()
        )
        result = get_offer_info(vk_user_id, offer)
    return result


def get_favorite(vk_user_id):
    with Session() as session:
        offer = (
            session.query(
                m.Offer.vk_offer_id,
                m.Offer.first_name,
                m.Offer.last_name,
                m.Offer.profile_link,
            )
            .join(m.UserOffer, m.UserOffer.vk_offer_id == m.Offer.vk_offer_id)
            .join(m.User, m.User.vk_user_id == m.UserOffer.vk_user_id)
            .filter(m.User.vk_user_id == vk_user_id)
            .filter(m.UserOffer.favorite_list == 1)
            .filter(m.UserOffer.black_list == 0)
            .all()
        )
        result = get_offer_info(vk_user_id, offer)
    return result


session.close()