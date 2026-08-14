from pydantic import Field, BaseModel
from typing import Annotated, List, Optional


class AuthorModel(BaseModel):

    """Sub-model for the authors list in the ranking response."""
    name: str
    link: Optional[str] = None


class RankingResponse(BaseModel):
    """

    Expected server response:

    ranking_response = [{
            "score": 0.7821,
            "title": "A Cross-Sectional Study of Postgraduate Students' Mental Well-Being: Exploring the Relationship Between Mental Well-Being, Perceived Stress, Academic Self-Efficacy, and Self-Efficacy for Self-Regulated Learning",
            "title_link": "https://pureportal.coventry.ac.uk/en/publications/a-cross-sectional-study-of-postgraduate-students-mental-well-bein/",
            "authors": [
                {
                    "name": "Bisal, N.",
                    "link": null
                },
                {
                    "name": "Brookes-Smith, C.",
                    "link": "https://pureportal.coventry.ac.uk/en/persons/celine-brookes-smith/"
                },
                {
                    "name": "Patel, R., Sharp, S.",
                    "link": null
                },
                {
                    "name": "Lycett, D.",
                    "link": "https://pureportal.coventry.ac.uk/en/persons/deborah-lycett/"
                },
                {
                    "name": "Turner, A.",
                    "link": "https://pureportal.coventry.ac.uk/en/persons/andy-turner/"
                },
                {
                    "name": "Whelan, M.",
                    "link": "https://pureportal.coventry.ac.uk/en/persons/maxine-whelan/"
                }
            ],
            "publish_date": "May 2026",
            "journal_name": "In: Health Science Reports.",
            "journal_volume": "9",
            "number_of_pages": "15 p."
        }, 

        {
            "score": 0.6112,
            "title": "Age-and sex-specific percentile curves for the Test of Gross Motor Development from 7,263 children aged 3-5 years from 13 countries",
            "title_link": "https://pureportal.coventry.ac.uk/en/publications/age-and-sex-specific-percentile-curves-for-the-test-of-gross-moto/",
            "authors": [
                {
                    "name": "Martins, C., Webster, E. K., Romo-Perez, V., Salami, S., Lemos, L.",
                    "link": null
                },
                {
                    "name": "Duncan, M.",
                    "link": "https://pureportal.coventry.ac.uk/en/persons/michael-duncan/"
                },
                {
                    "name": "Bardid, F., Staiano, A. E., Okely, A., Kambas, A., Sääkslahti, A., Pesce, C., Honrubia-Montesinos, C., Magistro, D., Niemistö, D., Carlevaro, F., Magno, F., Nobre, G., Aires, Í. & Estevan, I.",
                    "link": null
                }
            ],
            "publish_date": "4 Jun 2026",
            "journal_name": "In: Journal of Motor Learning and Development.",
            "journal_volume": "14",
            "number_of_pages": "11 p."
        }]
    """
    score: float
    title: str
    title_link: Optional[str] = None
    authors: List[AuthorModel] = []
    publish_date: Optional[str] = None
    journal_name: Optional[str] = None
    journal_volume: Optional[str] = None
    number_of_pages: Optional[str] = None


class UserInputValidator(BaseModel):
    """
    Model for validating incoming search queries from users.

    Expected User query as input: 

    input = {
        "query": "A Conceptual Discussion on Decolonising Photovoice and Reflections on Its Practical Application"
    }
    """
    query: Annotated[str, Field(min_length=1, description="User query...", examples=[
        "A Conceptual Discussion on Decolonising Photovoice and Reflections on Its Practical Application",
        "A Cross-Sectional Study of Postgraduate Students' Mental Well-Being: Exploring the Relationship Between Mental Well-Being, Perceived Stress, Academic Self-Efficacy, and Self-Efficacy for Self-Regulated Learning",
        "A cross-cultural study on the career counseling service ecosystem: implications for higher education marketing"
    ])]
