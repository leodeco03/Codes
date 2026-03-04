%% ========================================================================
%  PLOT IMPULSE RESPONSE FUNCTIONS
%  ========================================================================
%  This script generates publication-quality IRF figures for the SOE-NK
%  model. Run this AFTER executing QuantProject.mod in Dynare.
%
%  Usage:
%    1. Run Dynare: dynare QuantProject.mod
%    2. Run this script: plot_irfs
%
%  Authors: Leonardo Decorte & Suasdey Chea
%  ========================================================================

%% Settings
T = 13;                     % IRF horizon (quarters)
tt = 1:T;                   % Time axis
saveFigs = true;            % Set to false to only display
figPath = '../figures/';    % Output folder for figures

% Create figures folder if it doesn't exist
if saveFigs && ~exist(figPath, 'dir')
    mkdir(figPath);
end

% Plot formatting
set(0, 'DefaultAxesFontSize', 10);
set(0, 'DefaultLineLineWidth', 1.5);
colors = struct('blue', [0 0.4470 0.7410], ...
                'red', [0.8500 0.3250 0.0980], ...
                'green', [0.4660 0.6740 0.1880]);

%% ========================================================================
%  Q1: BENCHMARK FOREIGN ECONOMY
%% ========================================================================

%% Q1(a) - Monetary Policy Shock
figure('Name', 'Q1(a) Monetary Policy Shock', 'Position', [100 100 900 700]);
sgtitle('Q1(a) – Monetary Policy Shock (+1\%)', 'FontSize', 14, 'FontWeight', 'bold');

subplot(3,3,1);
plot(tt, oo_.irfs.y_eps_m(1:T) * 100, 'Color', colors.blue);
title('Output $y_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,2);
plot(tt, oo_.irfs.c_eps_m(1:T) * 100, 'Color', colors.blue);
title('Consumption $c_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,3);
plot(tt, oo_.irfs.i_eps_m(1:T) * 100, 'Color', colors.blue);
title('Interest Rate $i_t$', 'Interpreter', 'latex'); ylabel('pp'); grid on;

subplot(3,3,4);
plot(tt, oo_.irfs.pi_eps_m(1:T) * 100, 'Color', colors.blue);
title('CPI Inflation $\pi_t$', 'Interpreter', 'latex'); ylabel('pp'); grid on;

subplot(3,3,5);
plot(tt, oo_.irfs.ec_eps_m(1:T) * 100, 'Color', colors.blue);
title('Depreciation $e^c_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,6);
plot(tt, oo_.irfs.e_level_eps_m(1:T) * 100, 'Color', colors.blue);
title('FX Level $e_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,7);
plot(tt, oo_.irfs.S_eps_m(1:T) * 100, 'Color', colors.blue);
title('Terms of Trade $S_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,8);
plot(tt, oo_.irfs.ca_eps_m(1:T) * 100, 'Color', colors.blue);
title('Current Account', 'Interpreter', 'latex'); ylabel('\% GDP'); grid on;

if saveFigs, exportgraphics(gcf, [figPath 'IRF_Q1a_monetary.png'], 'Resolution', 300); end

%% Q1(b) - Preference Shock
figure('Name', 'Q1(b) Preference Shock', 'Position', [100 100 900 700]);
sgtitle('Q1(b) – Preference Shock (+1\%)', 'FontSize', 14, 'FontWeight', 'bold');

subplot(3,3,1);
plot(tt, oo_.irfs.y_eps_z(1:T) * 100, 'Color', colors.blue);
title('Output $y_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,2);
plot(tt, oo_.irfs.c_eps_z(1:T) * 100, 'Color', colors.blue);
title('Consumption $c_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,3);
plot(tt, oo_.irfs.i_eps_z(1:T) * 100, 'Color', colors.blue);
title('Interest Rate $i_t$', 'Interpreter', 'latex'); ylabel('pp'); grid on;

subplot(3,3,4);
plot(tt, oo_.irfs.pi_eps_z(1:T) * 100, 'Color', colors.blue);
title('CPI Inflation $\pi_t$', 'Interpreter', 'latex'); ylabel('pp'); grid on;

subplot(3,3,5);
plot(tt, oo_.irfs.ec_eps_z(1:T) * 100, 'Color', colors.blue);
title('Depreciation $e^c_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,6);
plot(tt, oo_.irfs.g_eps_z(1:T) * 100, 'Color', colors.red);
title('Preference $g_t$ (shocked)', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,7);
plot(tt, oo_.irfs.e_level_eps_z(1:T) * 100, 'Color', colors.blue);
title('FX Level $e_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,8);
plot(tt, oo_.irfs.ca_eps_z(1:T) * 100, 'Color', colors.blue);
title('Current Account', 'Interpreter', 'latex'); ylabel('\% GDP'); grid on;

if saveFigs, exportgraphics(gcf, [figPath 'IRF_Q1b_preference.png'], 'Resolution', 300); end

%% Q1(c) - Risk Premium Shock
figure('Name', 'Q1(c) Risk Premium Shock', 'Position', [100 100 900 700]);
sgtitle('Q1(c) – Risk Premium Shock (+1\%)', 'FontSize', 14, 'FontWeight', 'bold');

subplot(3,3,1);
plot(tt, oo_.irfs.y_eps_tau(1:T) * 100, 'Color', colors.blue);
title('Output $y_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,2);
plot(tt, oo_.irfs.c_eps_tau(1:T) * 100, 'Color', colors.blue);
title('Consumption $c_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,3);
plot(tt, oo_.irfs.i_eps_tau(1:T) * 100, 'Color', colors.blue);
title('Interest Rate $i_t$', 'Interpreter', 'latex'); ylabel('pp'); grid on;

subplot(3,3,4);
plot(tt, oo_.irfs.pi_eps_tau(1:T) * 100, 'Color', colors.blue);
title('CPI Inflation $\pi_t$', 'Interpreter', 'latex'); ylabel('pp'); grid on;

subplot(3,3,5);
plot(tt, oo_.irfs.ec_eps_tau(1:T) * 100, 'Color', colors.blue);
title('Depreciation $e^c_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,6);
plot(tt, oo_.irfs.tau_eps_tau(1:T) * 100, 'Color', colors.red);
title('Risk Premium $\tau_t$ (shocked)', 'Interpreter', 'latex'); ylabel('pp'); grid on;

subplot(3,3,7);
plot(tt, oo_.irfs.e_level_eps_tau(1:T) * 100, 'Color', colors.blue);
title('FX Level $e_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,8);
plot(tt, oo_.irfs.ca_eps_tau(1:T) * 100, 'Color', colors.blue);
title('Current Account', 'Interpreter', 'latex'); ylabel('\% GDP'); grid on;

if saveFigs, exportgraphics(gcf, [figPath 'IRF_Q1c_riskpremium.png'], 'Resolution', 300); end

%% Q1(d) - Foreign Interest Rate Shock
figure('Name', 'Q1(d) Foreign Interest Rate Shock', 'Position', [100 100 900 700]);
sgtitle('Q1(d) – Foreign Interest Rate Shock (+1\%)', 'FontSize', 14, 'FontWeight', 'bold');

subplot(3,3,1);
plot(tt, oo_.irfs.y_eps_i_star(1:T) * 100, 'Color', colors.blue);
title('Output $y_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,2);
plot(tt, oo_.irfs.c_eps_i_star(1:T) * 100, 'Color', colors.blue);
title('Consumption $c_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,3);
plot(tt, oo_.irfs.i_eps_i_star(1:T) * 100, 'Color', colors.blue);
title('Interest Rate $i_t$', 'Interpreter', 'latex'); ylabel('pp'); grid on;

subplot(3,3,4);
plot(tt, oo_.irfs.pi_eps_i_star(1:T) * 100, 'Color', colors.blue);
title('CPI Inflation $\pi_t$', 'Interpreter', 'latex'); ylabel('pp'); grid on;

subplot(3,3,5);
plot(tt, oo_.irfs.ec_eps_i_star(1:T) * 100, 'Color', colors.blue);
title('Depreciation $e^c_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,6);
plot(tt, oo_.irfs.i_star_eps_i_star(1:T) * 100, 'Color', colors.red);
title('Foreign Rate $i^*_t$ (shocked)', 'Interpreter', 'latex'); ylabel('pp'); grid on;

subplot(3,3,7);
plot(tt, oo_.irfs.e_level_eps_i_star(1:T) * 100, 'Color', colors.blue);
title('FX Level $e_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,8);
plot(tt, oo_.irfs.ca_eps_i_star(1:T) * 100, 'Color', colors.blue);
title('Current Account', 'Interpreter', 'latex'); ylabel('\% GDP'); grid on;

if saveFigs, exportgraphics(gcf, [figPath 'IRF_Q1d_foreignrate.png'], 'Resolution', 300); end

%% Q3(a) - Foreign Output Shock (Floating)
figure('Name', 'Q3(a) Foreign Output Shock', 'Position', [100 100 900 700]);
sgtitle('Q3(a) – Foreign Output Shock (-5\%, Floating FX)', 'FontSize', 14, 'FontWeight', 'bold');

subplot(3,3,1);
plot(tt, oo_.irfs.y_eps_y_star(1:T) * 100, 'Color', colors.blue);
title('Output $y_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,2);
plot(tt, oo_.irfs.c_eps_y_star(1:T) * 100, 'Color', colors.blue);
title('Consumption $c_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,3);
plot(tt, oo_.irfs.i_eps_y_star(1:T) * 100, 'Color', colors.blue);
title('Interest Rate $i_t$', 'Interpreter', 'latex'); ylabel('pp'); grid on;

subplot(3,3,4);
plot(tt, oo_.irfs.pi_eps_y_star(1:T) * 100, 'Color', colors.blue);
title('CPI Inflation $\pi_t$', 'Interpreter', 'latex'); ylabel('pp'); grid on;

subplot(3,3,5);
plot(tt, oo_.irfs.ec_eps_y_star(1:T) * 100, 'Color', colors.blue);
title('Depreciation $e^c_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,6);
plot(tt, oo_.irfs.y_star_eps_y_star(1:T) * 100, 'Color', colors.red);
title('Foreign Output $y^*_t$ (shocked)', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,7);
plot(tt, oo_.irfs.e_level_eps_y_star(1:T) * 100, 'Color', colors.blue);
title('FX Level $e_t$', 'Interpreter', 'latex'); ylabel('\% dev'); grid on;

subplot(3,3,8);
plot(tt, oo_.irfs.ca_eps_y_star(1:T) * 100, 'Color', colors.blue);
title('Current Account', 'Interpreter', 'latex'); ylabel('\% GDP'); grid on;

if saveFigs, exportgraphics(gcf, [figPath 'IRF_Q3a_foreignoutput.png'], 'Resolution', 300); end

%% Summary Display
fprintf('\n========================================\n');
fprintf('IRF Figures Generated Successfully\n');
fprintf('========================================\n');
if saveFigs
    fprintf('Saved to: %s\n', figPath);
end
fprintf('\nShock summary (impact effects):\n');
fprintf('  Monetary (eps_m):     y = %+.4f%%, pi = %+.4f%%\n', ...
    oo_.irfs.y_eps_m(1)*100, oo_.irfs.pi_eps_m(1)*100);
fprintf('  Preference (eps_z):   y = %+.4f%%, c = %+.4f%%\n', ...
    oo_.irfs.y_eps_z(1)*100, oo_.irfs.c_eps_z(1)*100);
fprintf('  Risk premium (eps_tau): ec = %+.4f%%, i = %+.4f%%\n', ...
    oo_.irfs.ec_eps_tau(1)*100, oo_.irfs.i_eps_tau(1)*100);
fprintf('  Foreign rate (eps_i*):  ec = %+.4f%%, y = %+.4f%%\n', ...
    oo_.irfs.ec_eps_i_star(1)*100, oo_.irfs.y_eps_i_star(1)*100);
fprintf('========================================\n');
