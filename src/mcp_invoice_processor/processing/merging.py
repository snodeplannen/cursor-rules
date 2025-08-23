"""
Module voor het samenvoegen en ontdubbelen van partiële resultaten.
"""
from typing import List
from rapidfuzz import fuzz
from .models import CVData, WorkExperience, Education


def merge_partial_cv_data(partial_results: List[CVData]) -> CVData:
    """
    Voegt een lijst van partiële CVData-objecten samen tot één object.

    Args:
        partial_results: Lijst van partiële CV resultaten

    Returns:
        CVData: Samengevoegd CV object
    """
    if not partial_results:
        raise ValueError("Geen partiële resultaten om samen te voegen")

    # Start met het eerste resultaat als basis
    merged = partial_results[0].model_copy()

    # Voeg werkervaring samen
    all_experiences = []
    for result in partial_results:
        if result.work_experience:
            all_experiences.extend(result.work_experience)
    merged.work_experience = deduplicate_work_experience(all_experiences)

    # Voeg opleiding samen
    all_education = []
    for result in partial_results:
        if result.education:
            all_education.extend(result.education)
    merged.education = deduplicate_education(all_education)

    # Voeg vaardigheden samen
    all_skills = []
    for result in partial_results:
        if result.skills:
            all_skills.extend(result.skills)
    merged.skills = deduplicate_skills(all_skills)

    # Voor andere velden, gebruik de eerste niet-lege waarde
    for result in partial_results[1:]:
        if not merged.email and result.email:
            merged.email = result.email
        if not merged.phone_number and result.phone_number:
            merged.phone_number = result.phone_number
        if not merged.summary and result.summary:
            merged.summary = result.summary

    return merged


def deduplicate_work_experience(experiences: List[WorkExperience], threshold: int = 85) -> List[WorkExperience]:
    """
    Ontdubbeld een lijst van werkervaringen met fuzzy matching.

    Args:
        experiences: Lijst van werkervaringen
        threshold: Drempelwaarde voor fuzzy matching (0-100)

    Returns:
        List[WorkExperience]: Ontdubbelde lijst van werkervaringen
    """
    if not experiences:
        return []

    unique_experiences: List[WorkExperience] = []
    for exp in experiences:
        is_duplicate = False
        for unique_exp in unique_experiences:
            # Vergelijk op basis van een combinatie van functie en bedrijf
            str1 = f"{exp.job_title} {exp.company}".lower()
            str2 = f"{unique_exp.job_title} {unique_exp.company}".lower()
            if fuzz.ratio(str1, str2) > threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_experiences.append(exp)

    return unique_experiences


def deduplicate_education(education: List[Education], threshold: int = 85) -> List[Education]:
    """
    Ontdubbeld een lijst van opleidingen met fuzzy matching.

    Args:
        education: Lijst van opleidingen
        threshold: Drempelwaarde voor fuzzy matching (0-100)

    Returns:
        List[Education]: Ontdubbelde lijst van opleidingen
    """
    if not education:
        return []

    unique_education: List[Education] = []
    for edu in education:
        is_duplicate = False
        for unique_edu in unique_education:
            # Vergelijk op basis van graad en instelling
            str1 = f"{edu.degree} {edu.institution}".lower()
            str2 = f"{unique_edu.degree} {unique_edu.institution}".lower()
            if fuzz.ratio(str1, str2) > threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_education.append(edu)

    return unique_education


def deduplicate_skills(skills: List[str], threshold: int = 85) -> List[str]:
    """
    Ontdubbeld een lijst van vaardigheden met fuzzy matching.

    Args:
        skills: Lijst van vaardigheden
        threshold: Drempelwaarde voor fuzzy matching (0-100)

    Returns:
        List[str]: Ontdubbelde lijst van vaardigheden
    """
    if not skills:
        return []

    unique_skills: List[str] = []
    for skill in skills:
        is_duplicate = False
        for unique_skill in unique_skills:
            if fuzz.ratio(skill.lower(), unique_skill.lower()) > threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_skills.append(skill)

    return unique_skills
