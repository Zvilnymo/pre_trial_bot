import logging
from typing import Optional, List, Dict
from database import QuestionnaireAnswer, get_session, ClientCategory
from bot.utils.messages import QUESTIONNAIRE_QUESTIONS

logger = logging.getLogger(__name__)


class QuestionnaireService:
    @staticmethod
    def save_answer(telegram_id: int, question_number: int, answer_text: str) -> bool:
        """Save questionnaire answer"""
        try:
            with get_session() as session:
                # Check if answer already exists
                existing = session.query(QuestionnaireAnswer).filter(
                    QuestionnaireAnswer.telegram_id == telegram_id,
                    QuestionnaireAnswer.question_number == question_number
                ).first()

                if existing:
                    existing.answer_text = answer_text
                else:
                    answer = QuestionnaireAnswer(
                        telegram_id=telegram_id,
                        question_number=question_number,
                        answer_text=answer_text
                    )
                    session.add(answer)

                session.commit()
                logger.info(f"Saved answer for user {telegram_id}, question {question_number}")
                return True
        except Exception as e:
            logger.error(f"Error saving answer: {e}")
            return False

    @staticmethod
    def get_answers(telegram_id: int) -> Dict[int, str]:
        """Get all answers for user as dict {question_number: answer_text}"""
        try:
            with get_session() as session:
                answers = session.query(QuestionnaireAnswer).filter(
                    QuestionnaireAnswer.telegram_id == telegram_id
                ).order_by(QuestionnaireAnswer.question_number).all()

                return {answer.question_number: answer.answer_text for answer in answers}
        except Exception as e:
            logger.error(f"Error getting answers: {e}")
            return {}

    @staticmethod
    def get_answers_with_questions(telegram_id: int) -> List[tuple]:
        """Get answers with questions as list of (q_number, q_text, answer_text)"""
        try:
            answers_dict = QuestionnaireService.get_answers(telegram_id)
            result = []

            for q_num, answer_text in answers_dict.items():
                if q_num <= len(QUESTIONNAIRE_QUESTIONS):
                    q_text = QUESTIONNAIRE_QUESTIONS[q_num - 1]
                    result.append((q_num, q_text, answer_text))

            return result
        except Exception as e:
            logger.error(f"Error getting answers with questions: {e}")
            return []

    @staticmethod
    def determine_client_category(answers: Dict[int, str]) -> ClientCategory:
        """
        Determine client category based on answers:
        Q10 (crypto) = YES -> CRYPTO
        Q11 (MFO) = YES -> MFO
        Q12 (banks) = YES -> BANK
        Default -> BANK
        """
        # Question 10: crypto
        q10_answer = answers.get(10, "").lower()
        if q10_answer in ['так', 'yes', 'да', '+']:
            return ClientCategory.CRYPTO

        # Question 11: MFO
        q11_answer = answers.get(11, "").lower()
        if q11_answer in ['так', 'yes', 'да', '+']:
            return ClientCategory.MFO

        # Question 12: banks or default
        return ClientCategory.BANK

    @staticmethod
    def is_questionnaire_complete(telegram_id: int) -> bool:
        """Check if user has completed questionnaire (all 15 questions)"""
        try:
            answers = QuestionnaireService.get_answers(telegram_id)
            return len(answers) >= 15
        except Exception as e:
            logger.error(f"Error checking questionnaire completion: {e}")
            return False

    @staticmethod
    def get_answer(telegram_id: int, question_number: int) -> Optional[str]:
        """Get specific answer"""
        try:
            with get_session() as session:
                answer = session.query(QuestionnaireAnswer).filter(
                    QuestionnaireAnswer.telegram_id == telegram_id,
                    QuestionnaireAnswer.question_number == question_number
                ).first()

                return answer.answer_text if answer else None
        except Exception as e:
            logger.error(f"Error getting answer: {e}")
            return None


questionnaire_service = QuestionnaireService()
