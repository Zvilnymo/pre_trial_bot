# Document packages based on questionnaire answers
# Each package is a list of (document_name, is_required)

DOCUMENT_PACKAGES = {
    # Package 1: Military personnel
    1: [
        ("Довідка з УБКІ", True),
        ("Довідка ОК-5", False),
        ("Довідка ОК-7", False),
        ("Довідка (форма №5) — підтвердження проходження служби", True),
        ("Фото військового квитка (всі сторінки, окрім сторінки зі зброєю)", True),
        ("Витяг з наказу про прийняття на посаду", True),
        ("Посвідчення УБД", False),
        ("Довідка (форма №6)", False),
        ("ЕЦП", False),
    ],

    # Package 2: Spouse of military personnel
    2: [
        ("Довідка з УБКІ", True),
        ("Довідка ОК-5", False),
        ("Довідка ОК-7", False),
        ("Довідка (форма №5) — підтвердження проходження служби військовослужбовцем", True),
        ("Фото військового квитка військовослужбовця (всі сторінки, окрім сторінки зі зброєю)", True),
        ("Витяг з наказу про прийняття на посаду", True),
        ("Свідоцтво про шлюб", True),
        ("Витяг з ДРАЦС про реєстрацію шлюбу", False),
        ("Посвідчення УБД", False),
        ("Довідка (форма №6)", False),
    ],

    # Package 3: IDP (internally displaced person)
    3: [
        ("Довідка з УБКІ", True),
        ("Довідка ОК-5", False),
        ("Довідка ОК-7", False),
        ("Скріншоти з застосунку «Дія», що підтверджують статус ВПО", True),
    ],

    # Package 4: Property damage
    4: [
        ("Довідка з УБКІ", True),
        ("Довідка ОК-5", False),
        ("Довідка ОК-7", False),
        ("Документи, що підтверджують пошкодження нерухомості: фотоматеріали або офіційні акти / довідки", True),
    ],

    # Package 5: Disability
    5: [
        ("Довідка з УБКІ", True),
        ("Довідка ОК-5", False),
        ("Довідка ОК-7", False),
        ("Фото пенсійного посвідчення", True),
    ],

    # Package 6: Disability of close relatives
    6: [
        ("Довідка з УБКІ", True),
        ("Довідка ОК-5", False),
        ("Довідка ОК-7", False),
        ("Посвідчення або довідка про інвалідність родича", True),
    ],

    # Package 7: Surgeries
    7: [
        ("Довідка з УБКІ", True),
        ("Довідка ОК-5", False),
        ("Довідка ОК-7", False),
        ("Узагальнена медична картка / медичні виписки з печатками, що підтверджують проведення операцій", True),
    ],

    # Package 8: Chronic diseases
    8: [
        ("Довідка з УБКІ", True),
        ("Довідка ОК-5", False),
        ("Довідка ОК-7", False),
        ("Узагальнена медична картка / медичні виписки з печатками, що підтверджують захворювання", True),
    ],

    # Package 9: Other circumstances
    9: [
        ("Довідка з УБКІ", True),
        ("Довідка ОК-5", False),
        ("Довідка ОК-7", False),
        ("Документи у довільній формі, що підтверджують інші важливі обставини (пільги, життєві ситуації, фінансові труднощі тощо)", True),
    ],

    # Package 10: Cryptocurrency
    10: [
        ("Довідка з УБКІ", True),
        ("Довідка ОК-5", False),
        ("Довідка ОК-7", False),
        ("Договір позики у криптовалюті з особистого кабінету", True),
        ("Додаткові угоди (за наявності)", False),
    ],

    # Package 11: MFO
    11: [
        ("Довідка з УБКІ", True),
        ("Довідка ОК-5", False),
        ("Довідка ОК-7", False),
    ],

    # Package 12: Banks
    12: [
        ("Довідка з УБКІ", True),
        ("Довідка ОК-5", False),
        ("Довідка ОК-7", False),
    ],

    # Package 13: Court cases
    13: [
        ("Довідка з УБКІ", True),
        ("ЕЦП", False),
        ("Довідка ОК-5", False),
        ("Довідка ОК-7", False),
        ("Судові документи: ухвали, рішення, постанови, позовні заяви, інші процесуальні документи", True),
    ],

    # Package 14: Enforcement proceedings
    14: [
        ("Довідка з УБКІ", True),
        ("Довідка ОК-5", False),
        ("Довідка ОК-7", False),
        ("Скріншоти з застосунку «Дія», що підтверджують поточний стан виконавчого провадження та актуальну суму", True),
    ],
}


def get_required_documents(questionnaire_answers: dict) -> list:
    """
    Determine which document packages are needed based on questionnaire answers
    questionnaire_answers: dict with keys as question numbers (1-14) and values as answers

    Returns: list of (document_name, is_required) tuples (deduplicated)
    """
    required_packages = []

    # Map question number to package number
    # Questions 1-14 correspond to packages 1-14
    for q_num in range(1, 15):
        answer = questionnaire_answers.get(q_num, "").lower()

        # For questions 1-14 (yes/no questions)
        if q_num <= 14:
            if answer in ['так', 'yes', 'да', '+']:
                required_packages.append(q_num)

    # Collect all documents from required packages
    all_documents = {}

    for package_num in required_packages:
        if package_num in DOCUMENT_PACKAGES:
            for doc_name, is_required in DOCUMENT_PACKAGES[package_num]:
                # If document already exists, keep it as required if any package requires it
                if doc_name in all_documents:
                    all_documents[doc_name] = all_documents[doc_name] or is_required
                else:
                    all_documents[doc_name] = is_required

    # Convert to list of tuples
    result = [(doc_name, is_required) for doc_name, is_required in all_documents.items()]

    return result
