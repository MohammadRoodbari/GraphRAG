import textwrap

import langextract as lx
from langextract.factory import ModelConfig

from src.config.settings import settings

PROMPT_DESCRIPTION = textwrap.dedent("""
    You are extracting structured information from Persian (Farsi)
    legal / regulatory banking documents (circulars, instructions,
    bylaws, and laws related to anti-money laundering).

    Rules:
    1. Extract entities in the order they appear in the text.
    2. Every entity must have a `document_group` attribute that
       names the specific legal instrument it belongs to (e.g. the
       circular itself, or one of the numbered دستورالعمل /
       آیین‌نامه / قانون items it references). Use a short, stable,
       human-readable label for each instrument (e.g.
       "بخشنامه 90/41478" or "دستورالعمل شناسایی مشتریان خارجی").
    3. Do NOT translate extracted text — keep extraction_text in the
       original Farsi exactly as it appears in the source.
    4. Numbers, dates, and article/note references should be
       extracted as their own entities, not folded into other spans.
    5. If a sentence defines a term (اصطلاح), extract the term and
       its definition as two linked entities sharing the same
       document_group as the article they appear in.
    6. Use these extraction_class values only:
       - document_type      (نوع سند: بخشنامه، دستورالعمل، آیین‌نامه، قانون، تصویب‌نامه)
       - document_title     (عنوان سند، در صورت وجود)
       - reference_number   (شماره بخشنامه/دستورالعمل/تصویب‌نامه)
       - document_date      (تاریخ صدور یا تصویب، به شمسی)
       - issuing_authority  (نهاد یا اداره صادرکننده)
       - recipient          (مخاطب سند، مثل بانک‌ها یا موسسات اعتباری)
       - person             (نام اشخاص امضاکننده یا مسئول)
       - organization       (نام سازمان/نهاد اشاره‌شده در متن)
       - article            (شماره و محتوای خلاصه یک ماده)
       - note               (شماره و محتوای خلاصه یک تبصره)
       - legal_term         (اصطلاحی که تعریف می‌شود)
       - definition         (متن تعریف اصطلاح)
       - obligation         (تکلیف یا الزام مقرر شده)
       - deadline           (مهلت زمانی مقرر شده)
       - cross_reference    (ارجاع به سند یا قانون دیگر)
""").strip()

EXAMPLES = [
    lx.data.ExampleData(
        text=(
            "ﭘﻴﺮو ﺑﺨﺸﻨﺎﻣﻪ ﺷﻤﺎره 90/41478 ﻣﻮرخ 1390/2/26 ﺑﺎﻧﻚ ﻣﺮﻛﺰي ﺟﻤﻬﻮري "
            "اﺳﻼﻣﻲ اﻳـﺮان، ﺑﻪ ﭘﻴﻮﺳﺖ دﺳﺘﻮراﻟﻌﻤﻞ ﭼﮕﻮﻧﮕﻲ ﺷﻨﺎﺳﺎﻳﻲ ﻣﺸﺘﺮﻳﺎن ﺧﺎرﺟﻲ "
            "ﻣﻮﺳﺴﺎت اﻋﺘﺒﺎري در 22 ﻣﺎده و 14 ﺗﺒﺼﺮه اﺑﻼغ ﻣﻲﺷﻮد. "
            "ﻣﻮﺳﺴﺎت اﻋﺘﺒﺎري ﺑﺎﻳﺪ ﺣﺪاﻛﺜﺮ ﻇﺮف ﻣﺪت ﻳﻚ ﻣﺎه ﭘﺲ از اﺑﻼغ اﻳﻦ ﺑﺨﺸﻨﺎﻣﻪ "
            "ﺿﻮاﺑﻂ ﻣﺬﻛﻮر را اﺟﺮا ﻧﻤﺎﻳﻨﺪ. "
            "ﻣﺎده 1 ـ در اﻳﻦ دﺳﺘﻮراﻟﻌﻤﻞ، ﻣﻮﺳﺴﺎت اﻋﺘﺒﺎري: ﺑﺎﻧﻚﻫﺎ و ﻣﻮﺳﺴﺎت اﻋﺘﺒﺎري "
            "ﻏﻴﺮﺑﺎﻧﻜﻲ ﻛﻪ ﺑﻪ اﻣﺮ واﺳﻄﻪ ﮔﺮي وﺟﻮه اﻗﺪام ﻣﻲﻧﻤﺎﻳﻨﺪ."
        ),
        extractions=[
            lx.data.Extraction(
                extraction_class="document_type",
                extraction_text="ﺑﺨﺸﻨﺎﻣﻪ",
                attributes={"document_group": "بخشنامه 90/41478"},
            ),
            lx.data.Extraction(
                extraction_class="reference_number",
                extraction_text="90/41478",
                attributes={"document_group": "بخشنامه 90/41478"},
            ),
            lx.data.Extraction(
                extraction_class="document_date",
                extraction_text="1390/2/26",
                attributes={"document_group": "بخشنامه 90/41478"},
            ),
            lx.data.Extraction(
                extraction_class="issuing_authority",
                extraction_text="ﺑﺎﻧﻚ ﻣﺮﻛﺰي ﺟﻤﻬﻮري اﺳﻼﻣﻲ اﻳـﺮان",
                attributes={"document_group": "بخشنامه 90/41478"},
            ),
            lx.data.Extraction(
                extraction_class="document_type",
                extraction_text="دﺳﺘﻮراﻟﻌﻤﻞ ﭼﮕﻮﻧﮕﻲ ﺷﻨﺎﺳﺎﻳﻲ ﻣﺸﺘﺮﻳﺎن ﺧﺎرﺟﻲ ﻣﻮﺳﺴﺎت اﻋﺘﺒﺎري",
                attributes={"document_group": "دستورالعمل شناسایی مشتریان خارجی"},
            ),
            lx.data.Extraction(
                extraction_class="cross_reference",
                extraction_text="ﭘﻴﺮو ﺑﺨﺸﻨﺎﻣﻪ ﺷﻤﺎره 90/41478",
                attributes={"document_group": "دستورالعمل شناسایی مشتریان خارجی"},
            ),
            lx.data.Extraction(
                extraction_class="obligation",
                extraction_text="ﻣﻮﺳﺴﺎت اﻋﺘﺒﺎري ﺑﺎﻳﺪ ... ﺿﻮاﺑﻂ ﻣﺬﻛﻮر را اﺟﺮا ﻧﻤﺎﻳﻨﺪ",
                attributes={"document_group": "بخشنامه 90/41478"},
            ),
            lx.data.Extraction(
                extraction_class="deadline",
                extraction_text="ﺣﺪاﻛﺜﺮ ﻇﺮف ﻣﺪت ﻳﻚ ﻣﺎه ﭘﺲ از اﺑﻼغ اﻳﻦ ﺑﺨﺸﻨﺎﻣﻪ",
                attributes={"document_group": "بخشنامه 90/41478"},
            ),
            lx.data.Extraction(
                extraction_class="article",
                extraction_text="ﻣﺎده 1",
                attributes={"document_group": "دستورالعمل شناسایی مشتریان خارجی"},
            ),
            lx.data.Extraction(
                extraction_class="legal_term",
                extraction_text="ﻣﻮﺳﺴﺎت اﻋﺘﺒﺎري",
                attributes={"document_group": "دستورالعمل شناسایی مشتریان خارجی"},
            ),
            lx.data.Extraction(
                extraction_class="definition",
                extraction_text="ﺑﺎﻧﻚﻫﺎ و ﻣﻮﺳﺴﺎت اﻋﺘﺒﺎري ﻏﻴﺮﺑﺎﻧﻜﻲ ﻛﻪ ﺑﻪ اﻣﺮ واﺳﻄﻪ ﮔﺮي وﺟﻮه اﻗﺪام ﻣﻲﻧﻤﺎﻳﻨﺪ",
                attributes={"document_group": "دستورالعمل شناسایی مشتریان خارجی"},
            ),
        ],
    )
]


class EntityExtractor:
    """Runs langextract against raw document text and returns raw extractions."""

    def extract(self, raw_data: str) -> list:
        result = lx.extract(
            text_or_documents=raw_data,
            prompt_description=PROMPT_DESCRIPTION,
            examples=EXAMPLES,
            config=ModelConfig(
                model_id=settings.LLM_MODEL,
                provider="openai",
                provider_kwargs={
                    "api_key": settings.OPENAI_API_KEY,
                    "base_url": settings.OPENAI_BASE_URL,
                },
            ),
            max_char_buffer=6000,
            extraction_passes=2,
            show_progress=True,
        )
        return result.extractions