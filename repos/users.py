import uuid
import json

from sqlalchemy import and_
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta


from utils.logging import logger
from schemas.users import Account
from services.mailing import send_email
from models.models import Person, Wallet, Address, SocialMedia, Session


class UserRepo:
    @classmethod
    def otp_auth(cls, user_email, db):
        # authorize user sign in by mailing otp to email
        try:
            user = db.query(Person).filter(
                and_(
                    Person.email == user_email,
                    Person.site_env == 'Starwire'      
                )
            ).one_or_none()
            logger.info(f"user record: {user}")
            # check if existing user
            if user:
                # Generate a 4-digit OTP
                import secrets
                otp = secrets.randbelow(9000) + 1000
                current_time = datetime.now(timezone.utc)
                exp_time = current_time + timedelta(minutes=10)

                session_info = {
                    "otp": otp,
                    "exp": exp_time.isoformat()
                }

                # search for user session
                existing_session = db.query(Session).filter(Session.sid == user.id).first()

                if existing_session:
                    # update existing session
                    existing_session.data = json.dumps(session_info)
                    existing_session.updatedAt = current_time
                    db.commit()

                    # send otp to user email
                    email_subject = "Your Starwire One-Time Passcode"
                    email_body = (f"Your OTP is {otp}."
                                  "It will expire in 10 minutes."
                    )
                    send_email(to=user_email, subject=email_subject, body=email_body)

                    return {"detail": "OTP sent to your email."}
            else:
                email_subject = "Starwire Registration Required"
                email_body = ("Your do not have a Starwire account under this email. "
                              "Try another email or sign-up here: https://app.starwire.io/signup")
                send_email(to=user_email, subject=email_subject, body=email_body)
                
                return {"detail": "Email not registered. Please check your inbox for sign-up instructions."}
        
        except Exception as e:
            logger.error(f"An error occurred sending user email: {e}")
            db.rollback()
            raise HTTPException(
                status_code=500, 
                detail=(
                    "There was an issue processing your sign-in request.\n"
                    "Please select 'Resend' to try agaain.\n"
                    "If the issue persists please comeback and try again later."
                )
            )

        
    
    @classmethod
    def authorize_user_signin(cls, user_data, db):
        logger.info("Authorizing user login...")

        user_email = user_data.get("email")
        otp = user_data.get("otp")

        logger.info(f"Validating user email...\n")
        account = None

        try:
            # retrieve the user
            user = db.query(Person).filter(
                and_(
                    Person.email == user_email,
                    Person.site_env == 'Starwire'      
                )
            ).one_or_none()

            if not user:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="This email is not registered with an account."
                )

            session = db.query(Session).filter(Session.sid == user.id).first()

            if not session:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="No OTP session found for user."
                )
            
            session_data = json.loads(session.data)
            session_otp = session_data.get("otp")
            session_exp = session_data.get("exp")

            # check otp code and expiration
            if session_otp != int(otp):
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Invalid OTP Code."
                )
            
            # check OTP expiration by converting the stored ISO timestamp to datetime
            exp_time = datetime.fromisoformat(session_exp)
            current_time = datetime.now(timezone.utc)

            if current_time > exp_time:
                db.rollback()
                raise HTTPException(
                    status_code=401,
                    detail=(
                        "OTP Code has expired.\n",
                        "Please request a new code."
                    )
                )

            logger.info("Pulling user profile for login...\n")
            # set up session
            session_token = str(uuid.uuid4())

            session.updatedAt = current_time
            session.expires = current_time + timedelta(hours=24)
            session.data = json.dumps({"session_token": session_token})           

            wallet = db.query(Wallet).filter(Wallet.people_id == user.id).first()

            db.commit()

            account = Account (
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone if user.phone else None,
                wallet=wallet.wallet if wallet else None,
            )

            logger.info("Authentication successful! User profile retrieved.")
            return account, session_token

        except Exception as e:
            db.rollback()
            logger.error(f"An error occurred signing user in: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An error occurred during sign in.\nPlease try again")
    

    @classmethod
    def reigster_user(cls, user_data, db):
        try:
            logger.info("Registering users info...")
            user_email = user_data.get('email')

            # check if person exists already
            person = db.query(Person).filter(
                Person.email == user_email,
                Person.site_env == 'Starwire'   
            ).one_or_none()
            
            # if no person
            if not person:
                person = Person(
                    email=user_email,
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'),
                    phone=user_data.get('phone'),
                    role='User',
                    site_env='Starwire'
                )

                db.add(person)
                db.flush()

                user_wallet = user_data.get('wallet')
                new_wallet = None
                person.phone = user_data.get('phone');

                if user_wallet:
                    wallet = db.query(Wallet).filter(Wallet.wallet == user_wallet).one_or_none()

                    if wallet:
                        raise HTTPException(
                            status_code=400,
                            detail="Your given wallet address is already tied to an account."
                        )
                    
                    new_wallet = Wallet(
                        wallet=user_wallet,
                        people_id=person.id,
                        type='HUMAN'
                    )    
                    db.add(new_wallet)
                    db.flush()
                
                logger.info("Checking address data...")
                address_fields = ['city', 'state', 'posta_code', 'country']
                # if any address details provided
                if any(user_data.get(field) for field in address_fields):
                    address = Address(
                        people_id=person.id,
                        address1=user_data.get('address'),
                        city=user_data.get('city'),
                        state=user_data.get('state'),
                        postal_code=user_data.get('postal_code'),
                        address_type='Home',
                        country=user_data.get('country')
                    )
                    db.add(address)

                logger.info("Checking socials data...")
                # if any social media accounts provided
                if user_data.get('socials'):
                    for social in user_data.get('socials'):
                        new_social = SocialMedia(
                            URL=social.get('url'),
                            app_name=social.get('platform'),
                            user_name=social.get('username'),
                            people_id=person.id      
                        )
                        db.add(new_social)
        
                # generate new session
                session_token = str(uuid.uuid4())
                current_time = datetime.now(timezone.utc)

                # store session
                session = Session(
                    sid=person.id,
                    data=json.dumps({"session_token": session_token}),
                    createdAt=current_time,
                    updatedAt=current_time,
                    expires=current_time + timedelta(hours=24)
                )
                
                db.add(session)
                db.commit()
                logger.info("User registered successfully!")

                account = Account (
                    email=person.email,
                    first_name=person.first_name,
                    last_name=person.last_name,
                    phone=person.phone if person else None,
                    wallet=new_wallet.wallet if new_wallet else None,
                )
                return account, session_token
            else:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="This email is already registered. Please signin or try a different email."
                )
         
        except HTTPException as http_e:
            db.rollback()
            raise http_e

        except Exception as e:
            db.rollback()
            logger.error(f"An unexpected error occurred during registration", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred. Please try again."
            )