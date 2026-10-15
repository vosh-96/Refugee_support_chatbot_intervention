# Refugee Support Chatbot Intervention

## Repository structure

```
.
├── Preregistration/
│   ├── Study1_preregistration.pdf
│   ├── Study2_preregistration.pdf
│   └── Study3_preregistration.pdf
├── Study_1/
│   ├── analysis/                 # Study1_analysis.Rmd + confirmatory figure (PDF)
│   ├── chatbot_implementation/   # Streamlit app + Google Sheets logger
│   └── data/                     # Pre/post Qualtrics exports (CSV) + chat logs (XLSX)
├── Study_2/
│   ├── anlaysis/                 # Study2_analysis.Rmd + confirmatory figure (PDF)
│   ├── chatbot_implementation/
│   └── data/
├── Study_3/
│   ├── analysis/                 # study3_analysis.Rmd + follow-up figures (PDF)
│   ├── chatbot_implementation/
│   ├── data/                     # Pre/post exports + chat logs
│   └── follow_up/data/           # Two-week follow-up export
└── Refugee_support_chatbot_intervention.Rproj
```

### Data files

| File type | Contents |
|---|---|
| `*Pre_Refugee_Attitude_Study*.csv` | Raw Qualtrics export of the pre-survey (consent, demographics, baseline attitudes) |
| `*Post_Refugee_Attitude_Study*.csv` | Raw Qualtrics export of the post-survey (attitudes, attention check, open-ended reflection, perceptions of the bot) |
| `FollowUp_Refugee_Attitude_Study_*.csv` | Study 3 two-week follow-up survey |
| `Chatbot_data_collection_*.xlsx` | Chat logs from the Streamlit app: one row per exchange, with `session_id`, `prolific_pid`, `timestamp`, `user_message`, `bot_message`, `condition` |

Participants are identified by their Prolific ID, which links the pre-survey, chat log, post-survey and (in Study 3) follow-up. The analysis scripts replace these with anonymised IDs during cleaning.

## Chatbot implementation

`chatbot_implementation/` contains the Streamlit app used for each study and a small logger that writes every exchange to a Google Sheet.

- **LLM**: `openai/gpt-oss-20b`, served through the [Together AI](https://www.together.ai/) API.
- **Conversation length**: seven rounds for the four treatment chatbots, five for the neutral chatbot; the flyer condition shows the fact sheet with no chat.
- **Flow**: the app reads `PROLIFIC_PID`, `STUDY_ID`, `SESSION_ID` and `BOT_NAME` (the assigned condition) from the URL, runs the conversation, and at the end links the participant to the Qualtrics post-survey with those IDs and the condition passed along as `BOT_TYPE`.
- **Testing**: adding `enable_selection=1` to the URL shows a dropdown for choosing any condition by hand.

The app is the same across studies except for the post-survey link.

### Running the app locally

1. Install dependencies:
   ```bash
   pip install streamlit together gspread requests
   ```
2. The app imports the logger as `gsheet_logger`, so copy or rename the dated logger file in the same folder:
   ```bash
   cp gsheet_logger_March31.py gsheet_logger.py   # or gsheet_logger_April6.py in Study_2
   ```
3. Create `.streamlit/secrets.toml` with your own credentials:
   ```toml
   TOGETHER_API_KEY = "your-together-api-key"

   [gcp_service_account]
   # Google service-account JSON fields (type, project_id, private_key, client_email, ...)
   ```
   The service account needs edit access to the Google Sheet set in `SHEET_URL` at the top of the app; point that at your own sheet.
4. Start the app and choose a condition:
   ```bash
   streamlit run streamlit_chatbot_prototype_app_March31.py
   ```
   Then open `http://localhost:8501/?enable_selection=1`, or `http://localhost:8501/?BOT_NAME=empathy` to load one condition directly.

## Reproducing the analyses

Each study has a self-contained R Markdown file that cleans the raw exports, applies the preregistered exclusions, builds the three attitude indices, fits the confirmatory models and produces the tables and figures.

1. Open `Refugee_support_chatbot_intervention.Rproj` in RStudio.
2. Install the required packages:
   ```r
   install.packages(c(
     "tidyverse", "readxl", "janitor", "lubridate", "purrr",
     "lme4", "lmerTest", "emmeans", "effectsize", "broom", "broom.mixed",
     "psych", "corrplot", "ggdist", "ggstatsplot", "patchwork",
     "knitr", "kableExtra", "tidytext", "topicmodels"
   ))
   ```
3. Knit the `.Rmd` in the study's analysis folder. The scripts read data with relative paths (`../data/...`), so the working directory must be the analysis folder itself, which is the default when knitting.

Knitting produces an HTML report, regenerates the PDF figures, and writes LaTeX and CSV tables to a `tables/` subfolder.
