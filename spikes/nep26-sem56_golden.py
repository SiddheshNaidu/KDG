"""Throwaway: writes tests/golden/nep26-sem56/*.json (DRAFT, hand-drafted topic lists) and validates topics with spikes/topic_validity.py.
Command: PYTHONIOENCODING=utf-8 python spikes/nep26-sem56_golden.py"""
import json, os, sys
sys.path.insert(0, "spikes")
import importlib
M = importlib.import_module("nep26-sem56_modules")
P = M.P
TV = importlib.import_module("topic_validity")
FAM = "nep26-sem56"
PDF = "data/raw/_unclassified/SEM-V.pdf"
S = lambda x: [t.strip() for t in x.split("|") if t.strip()]

G = {}
G["2165111"] = ("Statistics for Machine Learning and Data Science", [
    ("I", "Statistical Foundations, Covariance, and Sampling", S("Types of data|Descriptive statistics|Central tendency|Dispersion|Skewness|Kurtosis|Data visualization|Histograms|Boxplots|Scatter plots|Pair plots|Probability distributions|Normal distribution|Binomial distribution|Poisson distribution|Exponential distribution|Uniform distribution|Beta distribution|Gamma distribution|Covariance|Correlation|Confounding|Correlation matrices|Distance measures|Euclidean distance|Manhattan distance|Cosine distance|Sampling techniques|Simple random sampling|Stratified sampling|Cluster sampling|Central Limit Theorem|Law of Large Numbers|Data preprocessing|Handling missing values|Outlier treatment|Encoding|Normalization")),
    ("II", "Statistical Inference, Estimation & Resampling", S("Point estimates|Properties of estimators|Bias|Variance|Mean squared error|Maximum Likelihood Estimation|Method of Moments|Confidence intervals|Hypothesis testing|z-test|t-test|Chi-square test|ANOVA|Nonparametric tests|Mann-Whitney U test|Kruskal-Wallis test|Resampling methods|Bootstrap confidence intervals|Permutation tests|Likelihood Ratio Tests|Multiple testing correction|Bonferroni correction|False discovery rate|Monte Carlo simulation")),
    ("III", "Regression Models, Regularization & Nonlinear Models", S("Simple linear regression|Multiple linear regression|Model assumptions|Residual analysis|Multicollinearity|Variance inflation factor|Leverage|Cook's distance|Polynomial regression|Interaction effects|Nonlinear regression models|Regularization|Ridge regression|Lasso regression|Elastic Net|Spline regression|LOESS|Generalized Linear Models|Logistic regression|Poisson regression|Model evaluation metrics|MAE|MSE|RMSE|R-squared|Adjusted R-squared|Subset selection|Forward selection|Backward selection|Model calibration|Model interpretability")),
    ("IV", "Classification & Supervised Learning", S("Classification metrics|Accuracy|Precision|Recall|F1 score|ROC-AUC|PR curves|Logistic regression|Odds ratio|Decision boundary|Naive Bayes|k-NN classifier|Decision trees|Tree pruning|Ensemble methods|Bagging|Random Forest|Gradient Boosting|Support Vector Machines|Kernel trick|Imbalanced data handling|SMOTE|Class weights|Stratified splits|Confusion matrix analysis|Error trade-offs|Platt scaling|Isotonic regression")),
    ("V", "Unsupervised Learning & Dimensionality Reduction", S("PCA|Covariance matrix|Eigen decomposition|Explained variance|LDA|Kernel PCA|ICA|Clustering|K-means|Hierarchical clustering|DBSCAN|Cluster evaluation|Silhouette score|Davies-Bouldin index|Dimensionality reduction for visualization|t-SNE|UMAP|Outlier detection|Z-score method|IQR method|Isolation Forest|Local Outlier Factor")),
    ("VI", "Model Evaluation, Bayesian Inference & Ethics", S("Model selection|AIC|BIC|Bias-variance trade-off|Cross-validation|k-fold cross-validation|LOOCV|Repeated cross-validation|Calibration curves|Brier score|Bayesian fundamentals|Prior|Likelihood|Posterior|MAP estimation|MLE|Conjugate priors|Beta-Bernoulli model|Normal-Normal model|Naive Bayes from Bayesian perspective|Interpretability tools|SHAP|LIME|PDP|ICE|Fairness in ML|Equalized odds|Demographic parity|Ethical considerations|Model bias|Transparency|Data leakage|Data privacy|Anonymization|Differential privacy|Reproducible ML|Dataset versioning|MLflow|Weights and Biases")),
])
G["2166116"] = ("Edge Computing", [
    ("I", "Introduction to Cloud Computing, Fog Computing And Edge Computing", S("Cloud computing|Cloud computing latency limitations|Round trip time|Fog computing|Edge computing|Moving cloud services to the edge")),
    ("II", "IoT and Edge Architecture", S("IoT ecosystem|Device-to-cloud communication models|Sensors|Gateways|Cloud in IoT|IoT edge architecture components|Data flow in IoT edge architecture|IoT devices|Edge nodes|Communication interfaces|Cloud integration")),
    ("III", "Introduction to Raspberry Pi", S("Raspberry Pi|Evolution of Raspberry Pi boards|Raspberry Pi features and capabilities|Raspberry Pi board layout|GPIO pinouts|Hardware components|Interfaces|Peripheral connectivity|Operating systems on Raspberry Pi|SSH|Remote access tools|VNC|PuTTY|VS Code Remote|Remote file transfer")),
    ("IV", "Interfacing Raspberry Pi & Edge - to - Cloud Protocols", S("DHT temperature-humidity sensor interfacing|Reading sensor values|Data logging|Real-time monitoring|Lightweight IoT protocols|MQTT|CoAP|HTTP|Protocol comparison|MQTT architecture|MQTT workflow|MQTT packet structure|MQTT data formats")),
    ("V", "Edge Computing With Raspberry Pi", S("Edge computing fundamentals|Low-latency processing|Edge versus cloud computing|Raspberry Pi as edge device|Data acquisition|Local processing|Edge-Fog-Cloud hierarchy|Edge deployment models")),
    ("VI", "Applications of Edge Computing", S("Edge computing use cases|Smart cities|Industrial automation|Healthcare|Transportation|Agriculture|Retail|Edge nodes for video analytics|Environmental monitoring|Energy management|Autonomous systems")),
])
G["IKS501"] = ("Indian Knowledge System", [
    ("I", "Acoustic Science in Vedic Chanting and Indian Music", S("Nada (sound)|Shruti|Frequency, pitch and harmonic content|Shruti system|Frequency discrimination|Resonance|Architectural acoustics|Temple architecture and echo control|Natural acoustic amplification|Reverberation time|Standing waves|Structured sound encoding in Vedic recitation|Pada, Krama and Ghana patha|Built-in redundancy|Error detection and correction|Redundancy in digital communication")),
    ("II", "Tradition", S("IKS in renewable energy|Ancient Indian use of renewable energy|Solar architecture|Solar heating systems|Ancient windmills|Wind-powered water lifting|Ancient watermills|Irrigation systems|Biomass fuel|Bioenergy production|Integration of traditional knowledge with modern technologies|Gujarat windmills|Watermills in the Indus Valley|Konark Sun Temple")),
    ("III", "Linguistics, Number Systems, and rainfall Prediction", S("Components of language|Panini's work on Sanskrit grammar|Sanskrit in natural language processing|Number system in India|Decimal system|Katapayadi system|Pingala and the binary system|Units of measurement|Rainfall prediction techniques|Elements of the Indian calendar|Panchang and Nakshatras|Non-bio indicators|Bio indicators")),
    ("IV", "Mathematics Foundations in Ancient India and Its Relevance to Information Technology", S("Historical context of number ideas|Development of numeration|Zero as placeholder and number|Decimal place value|Major contributors to Indian mathematics|Procedural mathematics|Algorithmic thinking|Flowcharts|Decomposition|Computational logic|Modular arithmetic|Binary-style ideas|Data representation|Clock arithmetic|Remainders|Cyclic reasoning|Bits and bytes|Binary conversion|Checksums and parity|Simple cryptography")),
    ("V", "Indian Logic and its applications in Information Technology", S("Indian logic|Language and computation|Knowledge organization|Data and decision-making|Ethics and society|Sustainability|Responsible digital systems|IKS-inspired application design")),
    ("VI", "Sanskrit Grammar and Computational Modules", S("Sanskrit as structured language|Sounds|Words|Roots|Suffixes|Sandhi|Sentence structure|Paninian grammar|Rule-based grammar systems|Tokenization|Morphology|Parsing|Language rules|NLP examples|Sanskrit digital tools")),
])
G["2165119"] = ("Agile Software Development & DevOps Lab", [
    ("I", "Agile Project Management & DevOps Integration", S("Agile|Scrum|Jira|Agile project lifecycle management|Epics|User stories|Tasks|Sprints|Sprint planning|Sprint progress tracking|Jira integration with CI/CD pipelines|Agile reporting|Burndown chart|Velocity chart")),
    ("II", "Version Control & Collaboration using Git", S("Git|GitHub|Basic Git operations|Clone|Commit|Push|Pull|Branching strategies|Merging|Git workflows|Feature branching|Git Flow|Merge conflicts|GitHub Actions")),
    ("III", "CI/CD Automation using Jenkins & Containerization using Docker", S("CI/CD|DevOps pipelines|Jenkins|Jenkins job creation|GitHub webhook integration|CI pipeline|Docker fundamentals|Images|Containers|Dockerfiles|Multi-service deployment|Docker Compose")),
    ("IV", "Configuration Automation, Orchestration & Cloud Provisioning", S("Ansible|Inventory|Playbooks|Roles|Application provisioning|Application configuration|Kubernetes|Pods|Deployment|Service|Ingress|Containerized app management|Terraform|Providers|Resources|State files|Cloud infrastructure automation")),
    ("V", "Monitoring, Serverless Computing & MLOps Fundamentals", S("Monitoring tools|Prometheus|Grafana|Nagios|Exporters|Dashboards|Alerting|AWS Lambda|MLOps lifecycle|MLflow|Tracking ML runs|Model versioning and deployment|Airflow|DAGs|Tasks|Operators|Scheduling")),
    ("VI", "End-to-End DevOps Pipeline", S("DevOps automation pipeline design|Agile to monitoring integration|Cloud deployment|AWS|GCP|Azure|Pipeline security|DevSecOps")),
])
G["2165117"] = ("Statistics for Machine Learning and Data Science Lab", [
    ("E", "List of Experiments", S("Exploratory data analysis|Descriptive statistics|Histograms|Correlation matrix|Data preprocessing|Missing values|Encoding|Scaling|Outlier detection|Sampling methods|Simple random sampling|Stratified sampling|Cluster sampling|Central Limit Theorem|Hypothesis testing|t-test|Chi-square test|ANOVA|Bootstrap confidence intervals|Permutation tests|Maximum likelihood estimation|Linear regression|Regression diagnostics|VIF|Residual plots|Cook's distance|Ridge regression|Lasso regression|Elastic Net|Hyperparameter tuning|Classification models|Logistic regression|KNN|Naive Bayes|ROC analysis|Decision trees|Random Forest|Feature importance|PCA|K-means|Hierarchical clustering|SHAP|LIME|PDP|ICE|Fairness and bias detection metrics|Equalized odds|Demographic parity")),
    ("A", "List of Assignments / Tutorials", S("Machine learning pipeline|Resampling methods comparison|Bootstrap|Permutation tests|Regularization comparison|Bias-variance tradeoff|Ethical machine learning|Fairness|Interpretability|Transparency")),
])

pages = P.load()
segs, first = P.segments(pages)
d = {c: (s, e) for c, s, e in segs}
os.makedirs("tests/golden/" + FAM, exist_ok=True)
viol = {}
for code, (title, mods) in G.items():
    s, e = d[code]
    pgs = []
    L = P.lines_of(pages, s, e)
    if code in ("2165117",):
        pgs = [36, 37]
    else:
        if any(P.DS.match(l) for _, _, l in L):
            rows = M.parse(L)[0]
            pgs = sorted(set([first[code][0]] + [p for r in rows for p, n, x in r["lines"]] + [r["page"] for r in rows]))
    out = {"family": FAM, "course_code": code, "course_title": title, "source_pdf": PDF, "source_pages": pgs,
           "status": "DRAFT - needs human sign-off",
           "modules": [{"number": n, "name": nm, "topics": tp} for n, nm, tp in mods]}
    json.dump(out, open("tests/golden/%s/%s.json" % (FAM, code), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    for n, nm, tp in mods:
        for t in tp:
            v = TV.validate(t)
            if v: viol[(code, n, t)] = v
    print(code, len(mods), sum(len(m[2]) for m in mods), pgs)
for k, v in viol.items(): print("VIOL", k, v)
print("violations", len(viol))
