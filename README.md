# ![Project banner](resources/banner.png)

# EV Battery Health Prediction

## Background

The project aims to analyse the electric vehicle battery degradation and failure risks. With the increased production and sales of EVs (electric vehicles) and the high costs of a battery care is important to monitor degradation mechanisms in the battery and developing a prognostic models to predict its health is very vital. The idea is to be able to always be forecasting what is likely to happen over time, independent of any specific treatment. The primary objective of the project's idea was to be able to predict failure, but as the State of Health (SoH) related to the failures being in a clustered below a threshold we should also aim to be able to get close to the SoH targets with dataset.

## Data set content.

For this project the data source Kaggle.
The dataset tells us details about the chemistry, manufacturer, vehicle model and a series of readings gather about the state of the batteries including a state of health failure and risk and degradation category. We assume the health failure risk and degradation state have been provided by something that understands the factors already. The aim of the project is to bring together those factors to a risk matrix to evaluate what those state might be given the raw data. From this machine learning could be used to train a prognostic models to predict its health and risk factor.

## Business requirements and goals

Public safety to be able to quickly predict a battery state of health / degradation (long-term wear) alongside sudden failure risk (thermal runaway, internal short circuits, or sudden cell breakdown).
The vechicle safety standard authorities wish to finds positive coefficients in any of the data available to tell them which features identify issues and specifically leading to risks of failure.
The manufacturer has a business requirements are the find which features can lead to accelerated degradation, they may want to improve the chemistry or materials used that contribute to the degradation.

## What answers am I looking for from the dataset?

### Hypotheses:

**Hypothesis 1 ($H_1$)**: Internal Degradation & Resistance: (Degradation Category) Long-term physical wear metrics—specifically capacity_fade_pct, internal_resistance_mohm, total_energy_throughput_kwh, and cycle_count—will be the strongest predictors of the long-term degradation_category."Why: As batteries age, continuous chemical oxidation increases internal resistance and reduces total holding capacity. These are steady, cumulative metrics.

**Hypothesis 2 ($H_2$)**: Stress Factors & Thermal Anomaly Spikes: (Failure Risk Label) Operational stress spikes—specifically peak_temp_during_fast_charge_c, fast_charge_ratio, and high avg_ambient_temp_c—will be the primary drivers for predicting sudden failure_risk_label (e.g., Critical risk)."Why: A battery might have low overall wear (Normal degradation), but frequent fast charging in hot climates causes extreme thermal stress, leading to immediate high failure risk (like short circuits or cell swelling).

**Hypothesis 3 ($H_3$)**: Environmental & Usage Acceleration: Harsh operating conditions (high avg_depth_of_discharge_pct, high altitude_m, and extreme climate_zone temperatures) will accelerate the transition speed from Normal to Accelerated degradation."Why: Deep discharging and extreme temperatures degrade the internal battery chemistry faster than gentle usage cycles.

**Null Hypothesis ($H_0$)**: Irrelevant or Redundant Administrative Features: Static metadata and administrative features—specifically bms_firmware_version, service_count, vehicle_model, manufacturer, and date timestamps—will have no direct physical impact on battery failure or degradation."Why: While firmware or manufacturing batches can sometimes correlate with defects, raw administrative labels like vehicle_model or last_service_date do not directly cause electrochemical failure but some of the vehicle model may degr

## User Stories

A CEO (of a Battery maker firm), a Vehicle Safety Officer, and a EV car owner. What are the operational needs and expected outcomes?

I expect the dataset to tell us the consideration the effect of usage of EV cars in terms of the health of a battery in certain conditon..

#### What the CEO cares about:

- Warranty costs
- Fleet reliability
- Brand reputation
- Predictable maintenance
- Long‑term battery performance across models and manufacturers
  The dataset might offer this from better estimated of remaining cycles with Climate zone, temperature, humidity in certain areas as factors for marketing or research and development into battery manufacturering.

#### What the Safety Officer cares about:

- Preventing thermal events
- Identifying dangerous degradation patterns
- Monitoring high‑risk charging behaviour
- Detecting abnormal ageing before it becomes hazardous
  The data set might offer help in issuing acurate safety advice and guidlines to car buyer or car makers.

#### A car owner cares about:

- How long the battery will last
- How far they can drive and how often
- Whether their charging habits are harming the battery
- Whether their car is safe
- Which car to buy if they are considering EV cars or need to replace it
- Whether they should expect expensive repairs
- Detecting changes to the battery that are dinamially changing the battery reliability
- Risky patterns that could be reducing battery life

We don't of course aim to be able to solve all these aim but with research aim to predict the target general State of Health feature given the data available.
The dataset can train a model that provides health feedback from live BMS telemetry.
However, the model is limited to the measurements the BMS can collect continuously.
Some deeper diagnostic readings are only available during service events, meaning the model can update long‑term predictions only when those single, periodic observations are taken.

## Data set overview

We have 50,000 one row per battery observation that simulates realistic longitudinal health telemetry for EV battery packs across their service life. It covers the aging behavior for four common chemistries.
The battery dataset contains **35 columns** across 2,600 unique batteries (`battery_id`), each with ~10–40 longitudinal observations (`observation_id`) captured over its service life.

## EDA (Exploratory Data Analysis)

Exploring the data I can see that our dataset currently combines static battery metadata with time-series sensor telemetry in a single flat table. This structure causes data redundancy and missing values in static attributes across repeat readings. To fix this, we will normalize the dataset into two relational entities: a Batteries table for static properties (e.g., chemistry, capacity) and a BatteryReadings table for dynamic sensor observations, linked by a unique battery_id

BatteryTable: Contains 2,600 unique batteries keyed by battery_id across the 7 battery profile attributes (chemistry, manufacturer, vehicle_model, pack_capacity_kwh, manufacture_date, and climate_zone).
ReadingTable: Contains 50,000 unique telemetry observations keyed by observation_id across the 29 reading metrics and features (while retaining battery_id as a reference key so you can join them back when needed)

We now could be concerned that the unique telemetry observation keyed have some missing values which we could get back by averaging change over time. I have completed the grouped interpolation for cycle_count where it was simple to fill in missing values.
But we found missing values in other telemetry reading, to use "Regression Averages" fail for Health Readings because by filling missing health readings with global regression averages can be dangerous.Mean Imputation Blinds Your Anomaly Detection: If a battery experiences a dangerous temperature spike to $85^\circ\text{C}$ (peak_temp_during_fast_charge_c), but the next reading is NaN, filling it with the dataset average (say $35^\circ\text{C}$) hides the exact danger from the model for that reading. Smoothing Distorts Health Metrics: Health readings like internal_resistance_mohm or voltage_avg_v are volatile and non-monotonic. Unlike cycle_count, they fluctuate based on ambient temperature, current load, and immediate usage.

## Implementation and ETL stages. Step by step of ETL Exploratory_and_Visuals_notebook

1 After EDA we removed null values. I needed to see the columns with missing data. There are many! which could mean lots of work. 2. Because we're looking at observations over time, I concluded that it is best to delete everything that has no progression benefit, that missed three columns I considered essential. 5 rows were removed. 3. Because some row misses an 'easy fix' number of days we can just impute the missing 'days' values in a calculation with observation date. Because I'm planning to split the data set, we need to get this done early. 4. There are missing values which appear in another reading, because we have battery_id we can confidently fil it from that as it’s the same battery. We group by battery_id and complete all the null values for battery essentially chemistry as I predict it will be relevant. 5. Now the battery set is secure we can now split it by identification of features relating to the battery only and the observation reading values recorded. We now can work on Reading Table and BatteryTable to make it easier. 6. Now because there are so many missing records we decided we can fill many of them by understanding what they are if they're moving in a direction. At the point we involved an expert and presented the missing value in a bar chart. See 'Ask an expert'.

## Expert consultation: Adam Chikodi (Tata) — 8 October 2026

![WhatsApp chat with battery expert Adam Chikodi from Tata on 8 October 2026](jupyter_notebooks/Chat_Adam_Battery_Expert.png)

**Tip from Adam:** Distinguish direct indicators of a battery's current physical health, such as capacity fade and internal resistance, from behavioral inputs, such as energy throughput and fast-charge ratio, which describe the usage stresses that contributed to wear.

7. Impute battery readings. We gain knowledge from an expert to look at 5 features that they notice change in over time. We will fill missing values in the ReadingTable for those using moving average technique, where the rolling average function fill nulls. We group by battery_id being careful to retain the battery_id field in the dataset. Had to aligned to the rows return it afterwards due to how the group function worked.
8. We confirm the 5 features are now complete. We examine the data spread, by viewing.
   total_energy_throughput_kwh has large variance whereas the fast_charge_ratio hardly changes.
9. We can combine the tables again to view the features.
10. We visualise all the features and look for extreme colours of red or blue which illustrate positive or negative correlation in a Correlation matrix.
11. As we know the health of a battery will degrade over time, we create three basic charts to visualise the three target feature we're interested in State of Health and both risk of failure and degradation category.
    We quickly learn the thresholds from the boxplots. We'll need these later. They are 70% and 80% SoH.
12. We get the quartile statistics for those Health Boundaries and save them to output for later too.
13. We now focus in on a measured heatmap to give us score of Correlation matrix.
    We are looking for positive of negative which relates to SoH. We discover capacity_fade_pct is directly inertly related. Mathematically, Capacity Fade and State of Health ($\text{SoH}$) are exact two-way mirror reflections of each other: we therefore want to exclude it from the training and predict that also if needed.
14. We can use pandas to compute the correlation specifically with the target variable correlations from strongest to weakest and list them.
15. We are left with 3 features having dropped 2 looking at the heat map and the fade capacity score. We also have the chemistry which must be an important how a battery works. We predict that batteries of a similar chemical type will cluster together so the heat map matrix should be more defined.
16. We create Side-by-side subplots illustrate the degradation response across our four primary model features. The visual distributions confirm a clear linear relationship between increased operational wear and declining battery health. This shows that linear regression is a strong indicator to the type of model we will train.
17. We visualise the other feature we have ignored up until now just to have a reference to them. Almost sure we won't use them as part of the model.
18. Now we move into the feature selection proof. Silhouette Score evaluates two things simultaneously: Cohesion: How tight and close data points inside the same category are to each other. Separation: How far apart data points in one category are from data points in another category.
    Our score of $0.514$ is a Good/Reasonable structure. Groups are clearly formed, though some data points near the boundaries overlap slightly.
19. We can visualise those positive clusters and illustrate groupings
    Scatter plots group features by their predictive strength. A tightly defined trend—such as internal resistance—provides a clear signal for State of Health predictions, whereas heavily scattered metrics like fast charge ratio introduce operational noise.
20. The Scatter plots matrix (PairPlot) show Predictive Strength against the Target SoH Category: A feature's predictive strength measures how well it predicts the target variable ($\text{SoH}$). Plotting two input features against each other (e.g., internal_resistance vs. cycle_count) shows their correlation or interaction with one another.
21. This PairPlot utilizes continuous SoH as a coloured heat gradient across feature pairs. Clusters of low-health colour tones in high-resistance and high-cycle regions demonstrate clear feature-to-target predictive strength.
22. Two feature these two plots Battery Degradation Analysis by Chemistry Type against Cycle count and Resistance.
23. Two feature these two plots Battery Degradation Analysis by Chemistry Type against Age and Energy.
    Chemistry creates distinct branches: A linear model tries to fit a single straight line through all data points. However, because different battery chemistries (LFP, NMC, LMO) degrade at different rates, a single line fails.
    Tree-based decision rules: A Random Forest breaks the data down into branches based on feature values. It first branches by chemistry, and then applies specific degradation rules for that exact chemistry type.
24. Using the best feature if we train a mode we need to calculate the 'Mean Absolute Error' an dR² Score
    We do this by spitting our a train and test set which is used to first train then evaluate performance.
    Baseline Random Forest Performance ---
    Mean Absolute Error (MAE): 0.71%
    R² Score: 0.9792
25. The helpfulness of feature can be sorted by importances. We notice internal_resistance_mohm is by far the strongest.
26. Using a mathematics (Sigmoid Curves) to show how Probabilistic Logistic Risk Model driven by our feature internal_resistance_mohm is the single strongest driver of battery degradation, we mapped it directly to the absolute probability of crossing degradation thresholds of 70% and 80%.
27. We normalized the feature remaining and plotted heatmaps against the chemistry to show how the degradation risk faired.
28. We plotted the heatmaps against the manufacturer to show how the degradation risk faired.
29. We plot the distribution of the 4 features used in the training mode. Initially, extreme high values out in the long right tail (e.g., energy throughput $> 300,000\text{ kWh}$ or resistance $> 150\text{ m}\Omega$) look like potential outlier errors. However, we determined that these are not bad sentinels or data corruptions, but legitimate operational extremes representing heavily aged or heavily stressed battery cells.
30. After normalizing our primary features to a $0\text{--}1$ range, we exported the dataset to the main repository folder for Streamlit integration. Plotting normalized features together on a single line chart highlights relative changes across vastly different scales—providing an intuitive visual for how feature preprocessing affects model performance.

## Training Notebook

The training notebook follow the same data pipeline process of cleaning as the ETL notebook.

# Initial model creation

--- Model Evaluation ---
R² Score: 0.9830
Mean Absolute Error (MAE): 0.69%
pkl file was saved to this directory.
...\EV_Battery_Failure_Prediction\jupyter_notebooks\streamlit\rf_model.pkl

Problem encountered that it can't be uploaded to GitHub due to size limitations.
To get around it I uploade it to Hugging face's website instead.
https://huggingface.co/CodeInstitute/herokuapp_rf_model

# Building the Demo App, Interactive Dashboard

I used the multi-page Streamlit application example in the application we were given in the LMS.
I added the batteryFailurePrediction python file which add selectboxs for each feature I want in my demo.
I added the dashboard as a second page which loads Seaborn plots of the normalised and saved in step 30.

https://batteryhealthprediction-b788ac7e7f6c.herokuapp.com/

## Improving the model.

With our Tree-based decision rules: A Random Forest breaks the data down into branches based on feature values
we got a R² Score: 0.9830 and Mean Absolute Error (MAE): 0.69%.
How to improve it?
Hypothesis: By tuning max_features and increasing n_estimators on our core 4 main features, we decorrelate individual decision trees within the forest. This is because we are forcing individual trees to split on different feature subsets prevents dominant drivers (like internal resistance) from masking subtle interaction signals in cycle count and age, leading to a lower overall MAE

We can use a Grid Search tuning across 24 model combinations.
The GridSearchCV to pick the hyperparameter combination that minimizes absolute prediction error during cross-validation folds. It automatically retrieves the pipeline pre-loaded with the winning parameters so we don't have to rebuild it manually.

Job Uses all available processor cores on my computer to run cross-validation in parallel, speeding up execution is possible if I switch to Google Colab for faster GPU Access.

## Ethical consideration

## Reference and citations

## Conclusion.
