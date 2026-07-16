function results = train_model()
    % TRAIN_MODEL - Train ensemble architecture (RF, XGBoost, SVM) with cross-validation
    % Returns a struct with accuracy metrics
    
    fprintf('=== CardioScan AI Model Training ===\n');
    fprintf('Loading dataset...\n');
    
    data = readtable('heart.csv');
    data.target = categorical(data.target);
    
    n_records = height(data);
    fprintf('Dataset: %d records loaded\n', n_records);
    
    % Define predictor and response
    predictorNames = {'age','sex','cp','trestbps','chol','fbs','restecg','thalach','exang','oldpeak','slope','ca','thal'};
    X = data(:, predictorNames);
    Y = data.target;
    
    % ---- Random Forest (Bagging) ----
    fprintf('Training Random Forest Ensemble (Bagging, 50 cycles, regularized)...\n');
    t_rf = templateTree('Reproducible', true, 'MinLeafSize', 5);
    mdl_rf = fitcensemble(X, Y, 'Method', 'Bag', ...
        'NumLearningCycles', 50, ...
        'Learners', t_rf);
    
    % Cross-validation for RF
    cv_rf = crossval(mdl_rf, 'KFold', 5);
    acc_rf = 1 - kfoldLoss(cv_rf);
    fprintf('  RF 5-Fold CV Accuracy: %.2f%%\n', acc_rf * 100);
    
    % Feature importance for RF
    imp_rf = oobPermutedPredictorImportance(mdl_rf);
    
    % ---- XGBoost equivalent (LogitBoost) ----
    fprintf('Training XGBoost equivalent (LogitBoost, 50 cycles, regularized)...\n');
    t_xgb = templateTree('MinLeafSize', 5);
    mdl_xgb = fitcensemble(X, Y, 'Method', 'LogitBoost', ...
        'NumLearningCycles', 50, 'LearnRate', 0.1, 'Learners', t_xgb);
    
    % Cross-validation for XGBoost
    cv_xgb = crossval(mdl_xgb, 'KFold', 5);
    acc_xgb = 1 - kfoldLoss(cv_xgb);
    fprintf('  XGBoost 5-Fold CV Accuracy: %.2f%%\n', acc_xgb * 100);
    
    % Feature importance for XGBoost
    imp_xgb = predictorImportance(mdl_xgb);
    
    % ---- Kernel-based SVM (RBF) ----
    fprintf('Training Kernel-based SVM (RBF, regularized)...\n');
    mdl_svm = fitcsvm(X, Y, 'KernelFunction', 'rbf', ...
        'Standardize', true, ...
        'BoxConstraint', 0.5);
    
    % Cross-validation for SVM
    cv_svm = crossval(mdl_svm, 'KFold', 5);
    acc_svm = 1 - kfoldLoss(cv_svm);
    fprintf('  SVM 5-Fold CV Accuracy: %.2f%%\n', acc_svm * 100);
    
    % ---- Compute ensemble accuracy ----
    ensemble_acc = (acc_rf + acc_xgb + acc_svm) / 3;
    fprintf('\nEnsemble Average Accuracy: %.2f%%\n', ensemble_acc * 100);
    
    % ---- Compute healthy population means (target=1 in this dataset) ----
    low_risk_idx = data.target == '1';
    healthy_means = zeros(1, length(predictorNames));
    for i = 1:length(predictorNames)
        healthy_means(i) = mean(data{low_risk_idx, predictorNames{i}});
    end
    
    % ---- Combined feature importance ----
    feature_importance = (imp_rf + imp_xgb) / 2;
    % Normalize to sum to 1
    feature_importance = feature_importance / sum(feature_importance);
    
    % ---- Save model ----
    training_time = datetime('now', 'Format', 'yyyy-MM-dd HH:mm:ss');
    training_time_str = char(training_time);
    
    save('heart_ai_model.mat', 'mdl_rf', 'mdl_xgb', 'mdl_svm', ...
        'feature_importance', 'predictorNames', 'healthy_means', ...
        'acc_rf', 'acc_xgb', 'acc_svm', 'ensemble_acc', ...
        'n_records', 'training_time_str');
    
    fprintf('\nModel saved to heart_ai_model.mat\n');

    % ---- Visualize Training Results ----
    fprintf('Generating Training Performance Graph...\n');
    f = figure('Name', 'CardioScan AI Training Status', 'NumberTitle', 'off', 'Position', [100, 100, 1300, 450]);
    
    subplot(1, 3, 1);
    bar(feature_importance * 100, 'FaceColor', [0, 0.86, 0.91]); 
    title('Ensemble Feature Importance');
    set(gca, 'XTick', 1:13, 'XTickLabel', predictorNames);
    xtickangle(45);
    ylabel('Relative Importance (%)');
    grid on;
    
    subplot(1, 3, 2);
    models = {'Random Forest', 'XGBoost', 'SVM', 'Ensemble Avg'};
    accs = [acc_rf, acc_xgb, acc_svm, ensemble_acc] * 100;
    b = bar(accs);
    b.FaceColor = 'flat';
    b.CData(4,:) = [0, 0.86, 0.91]; % Highlight ensemble
    title(sprintf('5-Fold CV Accuracy (N=%d)', n_records));
    set(gca, 'XTick', 1:4, 'XTickLabel', models);
    xtickangle(45);
    ylabel('Accuracy (%)');
    ylim([max(0, min(accs)-5), 100]);
    grid on;
    
    % Add text labels on bars
    for i = 1:4
        text(i, accs(i) + 1, sprintf('%.1f%%', accs(i)), 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
    end

    subplot(1, 3, 3);
    err_rf = oobLoss(mdl_rf, 'Mode', 'cumulative');
    plot(err_rf * 100, 'LineWidth', 2.5, 'Color', [1 0.3 0.4]);
    title('Random Forest Learning Curve');
    xlabel('Number of Trees (Learning Cycles)');
    ylabel('Cumulative OOB Error (%)');
    grid on;

    drawnow;
    
    try
        saveas(f, 'model_training_graph.png');
        if exist('static', 'dir')
            saveas(f, 'static/model_training_graph.png');
        end
    catch
    end

    % Only close the figure if running headless (Python Engine)
    if ~usejava('desktop')
        close(f);
    end

    fprintf('=== Training Complete ===\n');
    
    % Return results as array for Python consumption
    results = [acc_rf * 100, acc_xgb * 100, acc_svm * 100, ensemble_acc * 100, n_records];
end