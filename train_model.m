data = readtable('heart.csv');
data.target = categorical(data.target);
% Train an Ensemble of Trees for high accuracy
mdl = fitcensemble(data, 'target', 'Method', 'Bag', 'NumLearningCycles', 50);
save('heart_ai_model.mat', 'mdl');
disp('AI Model trained and saved successfully.');