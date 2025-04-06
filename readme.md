# 📘 Restaurant Survival Analysis in Ho Chi Minh City
In today's landscape, a restaurant's survival and success are influenced by various factors, including operational efficiency and digital presence. This research integrates Aspect-Based Sentiment Analysis (ABSA) with Survival Analysis to explore the impact of customer sentiment on restaurant closures in Ho Chi Minh City, Vietnam.

## 📄 Table of Contents
- [� Restaurant Survival Analysis in Ho Chi Minh City](#-restaurant-survival-analysis-in-ho-chi-minh-city)
  - [📄 Table of Contents](#-table-of-contents)
  - [🔍 Overview](#-overview)
  - [✨ Key Features](#-key-features)
  - [📊 Data](#-data)
  - [🗂 Project Structure](#-project-structure)
  - [⚙️ Module Breakdown](#️-module-breakdown)
      - [🕸️ 0\_crawl](#️-0_crawl)
      - [💬 1\_absa](#-1_absa)
      - [📈 2\_survival](#-2_survival)
  - [📄 Note](#-note)

## 🔍 Overview
Utilizing a dataset of 18,060 customer reviews from 315 restaurants crawled from the Google Maps Platform, the study investigates how user-generated content and operational attributes contribute to restaurant longevity. A semi-supervised learning approach is applied to fine-tune the CafeBERT model, achieving an F1-score of **82.23%**.

Using the ABSA-enhanced CafeBERT model, sentiment is categorized into three core aspects: food, service, and atmosphere. These are incorporated into three survival models:

- Nonlinear Cox Proportional Hazards (N-CoxPH)
- Conditional Survival Forest (CSF)
- Neural Multi-Task Logistic Regression (N-MTLR)

Among these, N-CoxPH demonstrated the highest predictive performance, with a C-index of **93.35%** and IBS of **6.91%**.

## ✨ Key Features
- Cox Proportional Hazards model
- Log-rank test
- Time-varying covariates
- DeepSurv / ML-based survival models
- Custom visualizations (e.g., survival curves, hazard functions)

## 📊 Data
Source: Crawling from Google Maps Platform
Description: A dataset of 18,060 customer reviews from 315 restaurants

## 🗂 Project Structure

```
├── 0_crawl
│   ├── 0_prepare_data.ipynb
│   ├── 1_api_crawling.ipynb
│   └── 2_review_crawling.py
├── 1_absa
│   ├── 0_filter_data.ipynb
│   ├── 1_preprocessing_absa.ipynb
│   ├── 2_absa_join_model_training.ipynb
│   └── 3_absa_inference_remaining.ipynb
└── 2_survival
    ├── 0_preprocessing.ipynb
    ├── 1_survival_model.ipynb
    ├── 2_eda.ipynb
    └── 3_risk_score.ipynb
```

## ⚙️ Module Breakdown
#### 🕸️ 0_crawl  
Scripts and notebooks for data collection from the Google Maps Platform.
- **0_prepare_data.ipynb**: Initial data prep and cleaning.  
- **1_api_crawling.ipynb**: Crawls reviews and metadata via API.  
- **2_review_crawling.py**: Additional crawling and parsing logic.  

#### 💬 1_absa  
Aspect-Based Sentiment Analysis using CafeBERT.
- **0_filter_data.ipynb**: Filters reviews and prepares inputs.  
- **1_preprocessing_absa.ipynb**: Tokenization, label prep, formatting for BERT.  
- **2_absa_join_model_training.ipynb**: Trains CafeBERT with semi-supervised learning.  
- **3_absa_inference_remaining.ipynb**: Runs inference on unlabeled data.  

#### 📈 2_survival  
Survival modeling and analysis using sentiment features.
- **0_preprocessing.ipynb**: Merges features, prepares datasets.  
- **1_survival_model.ipynb**: Builds and compares N-CoxPH, CSF, and N-MTLR models.  
- **2_eda.ipynb**: Explores patterns in the data.  
- **3_risk_score.ipynb**: Computes risk scores based on model outputs.  

## 📄 Note
- Ensure access to the Google Maps API with appropriate billing.
- GPU is recommended for training BERT-based models.
