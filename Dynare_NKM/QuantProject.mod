%% ========================================================================
%  Small Open Economy New Keynesian Model
%  ========================================================================
%  Course: ECON6008 International Money and Finance
%  University of Sydney - Semester 2, 2025
%  
%  Authors: Leonardo Decorte & Suasdey Chea
%  Group: #21
%  
%  Description:
%  This model implements a linearized small open economy NK framework to
%  analyze the transmission of domestic and foreign shocks under different
%  exchange rate regimes. Key features include:
%    - Habit formation in consumption
%    - Calvo pricing with indexation
%    - UIP with risk premium
%    - Taylor rule with optional FX response
%
%  References:
%    - Galí & Monacelli (2005)
%    - Handout specifications
%  ========================================================================

%% ------------------------------------------------------------------------
%  1. ENDOGENOUS VARIABLES
%% ------------------------------------------------------------------------
var 
    % Domestic block
    c           $c_t$           (long_name='Consumption')
    y           $y_t$           (long_name='Output')
    i           $i_t$           (long_name='Nominal interest rate')
    pi          $\pi_t$         (long_name='CPI inflation')
    piH         $\pi^H_t$       (long_name='Domestic goods inflation')
    piF         $\pi^F_t$       (long_name='Imported goods inflation')
    S           $S_t$           (long_name='Terms of trade')
    q           $q_t$           (long_name='Real exchange rate')
    mc          $mc_t$          (long_name='Real marginal cost')
    a           $a_t$           (long_name='Net foreign assets')
    ec          $e^c_t$         (long_name='Nominal depreciation rate')
    e_level     $e_t$           (long_name='Nominal exchange rate level')
    ca          $ca_t$          (long_name='Current account')
    
    % Foreign block (exogenous AR(1) processes)
    y_star      $y^*_t$         (long_name='Foreign output')
    pi_star     $\pi^*_t$       (long_name='Foreign inflation')
    i_star      $i^*_t$         (long_name='Foreign interest rate')
    
    % Shock processes
    tau         $\tau_t$        (long_name='Risk premium')
    g           $g_t$           (long_name='Preference shock')
    epsH        $\varepsilon^H_t$ (long_name='Cost-push shock');

%% ------------------------------------------------------------------------
%  2. EXOGENOUS SHOCKS
%% ------------------------------------------------------------------------
varexo 
    eps_m           $\varepsilon^m_t$       (long_name='Monetary policy shock')
    eps_tau         $\varepsilon^\tau_t$    (long_name='Risk premium shock')
    eps_z           $\varepsilon^z_t$       (long_name='Preference shock')
    eps_H           $\varepsilon^{H}_t$     (long_name='Cost-push shock')
    eps_y_star      $\varepsilon^{y*}_t$    (long_name='Foreign output shock')
    eps_pi_star     $\varepsilon^{\pi*}_t$  (long_name='Foreign inflation shock')
    eps_i_star      $\varepsilon^{i*}_t$    (long_name='Foreign interest rate shock');

%% ------------------------------------------------------------------------
%  3. PARAMETERS
%% ------------------------------------------------------------------------
parameters 
    % Structural parameters
    sigma       $\sigma$        (long_name='Inverse IES')
    alpha       $\alpha$        (long_name='Import share / openness')
    epsilon     $\varepsilon$   (long_name='Elasticity of substitution (dom/for)')
    beta        $\beta$         (long_name='Discount factor')
    thetaH      $\theta_H$      (long_name='Calvo probability (domestic)')
    phi         $\phi$          (long_name='Risk premium elasticity')
    varphi      $\varphi$       (long_name='Inverse Frisch elasticity')
    h           $h$             (long_name='Habit formation')
    xi          $\xi$           (long_name='Preference shock elasticity')
    iotaH       $\iota_H$       (long_name='Price indexation')
    
    % Taylor rule coefficients
    rho_i       $\rho_i$        (long_name='Interest rate smoothing')
    phi_pi      $\phi_\pi$      (long_name='Inflation response')
    phi_y       $\phi_y$        (long_name='Output response')
    phi_dy      $\phi_{\Delta y}$ (long_name='Output growth response')
    phi_e       $\phi_e$        (long_name='Exchange rate response')
    
    % Shock persistence
    rho_tau     $\rho_\tau$     (long_name='Risk premium persistence')
    rho_g       $\rho_g$        (long_name='Preference shock persistence')
    rho_H       $\rho_H$        (long_name='Cost-push persistence')
    rho_y_star  $\rho_{y*}$     (long_name='Foreign output persistence')
    rho_pi_star $\rho_{\pi*}$   (long_name='Foreign inflation persistence')
    rho_i_star  $\rho_{i*}$     (long_name='Foreign interest rate persistence')
    
    % Composite parameters
    omega       $\omega$        (long_name='CPI-PPI wedge coefficient')
    psi         $\psi$          (long_name='TOT weight in resource constraint')
    kappaH      $\kappa_H$      (long_name='Phillips curve slope');

%% ------------------------------------------------------------------------
%  4. CALIBRATION
%% ------------------------------------------------------------------------
% Structural parameters
sigma   = 1;        % Log utility
alpha   = 0.24;     % Import share
epsilon = 0.85;     % Elasticity dom/for goods
beta    = 0.99;     % Quarterly discount factor
thetaH  = 0.75;     % Price stickiness (avg duration 4Q)
phi     = 0.01;     % Risk premium elasticity
varphi  = 1.26;     % Inverse Frisch
h       = 0.25;     % Habit formation
xi      = 0.15;     % Preference shock coefficient
iotaH   = 0.30;     % Price indexation

% Taylor rule (baseline)
rho_i   = 0.70;     % Smoothing
phi_pi  = 1.90;     % Inflation response (> 1 for determinacy)
phi_y   = 0.05;     % Output level response
phi_dy  = 0.55;     % Output growth response
phi_e   = 0.00;     % FX response (0 = pure float, >0 = managed float)

% Shock persistence
rho_tau     = 0.70;
rho_g       = 0.70;
rho_H       = 0.70;
rho_y_star  = 0.70;
rho_pi_star = 0.70;
rho_i_star  = 0.70;

% Composite parameters
kappaH = (1 - thetaH) * (1 - beta*thetaH) / thetaH;
omega  = alpha;
psi    = alpha * (epsilon - 1) / (1 - alpha);

%% ------------------------------------------------------------------------
%  5. MODEL EQUATIONS
%% ------------------------------------------------------------------------
model(linear);

% ---- Domestic Block ----

% (1) IS curve with habit formation and preference shock
c = (h/(1+h)) * c(-1) 
  + (1/(1+h)) * c(+1) 
  - (1/sigma) * ((1-h)/(1+h)) * (i - pi(+1)) 
  + xi * g;

% (2) Goods market clearing
y = (1 - alpha) * c + alpha * y_star + psi * (2 - alpha) * S;

% (3) Real exchange rate definition
q = (1 - alpha) * S;

% (4) Terms of trade dynamics
S - S(-1) = piF - piH;

% (5) Domestic Phillips curve with indexation
(piH - iotaH * piH(-1)) = beta * (piH(+1) - iotaH * piH) + kappaH * mc + epsH;

% (6) Real marginal cost
mc = varphi * y + psi * S + sigma * c;

% (7) CPI inflation (CPI-PPI wedge)
pi = piH + omega * (S - S(-1));

% (8) UIP with risk premium
i - i_star = ec(+1) - phi * a + pi(+1) + tau;

% (9) Current account / NFA accumulation
y - c = a - (1/beta) * a(-1) + (phi/(1 - alpha)) * q;

% (10) Imported goods inflation (LOP)
piF = ec + pi_star;

% (11) Taylor rule
i = rho_i * i(-1) 
  + phi_pi * pi 
  + phi_y * y 
  + phi_dy * (y - y(-1)) 
  + phi_e * ec 
  - eps_m;

% ---- Exogenous Processes ----

% (12) Risk premium AR(1)
tau = rho_tau * tau(-1) + eps_tau;

% (13) Preference shock AR(1)
g = rho_g * g(-1) + eps_z;

% (14) Cost-push shock AR(1)
epsH = rho_H * epsH(-1) + eps_H;

% (15) Foreign output AR(1)
y_star = rho_y_star * y_star(-1) + eps_y_star;

% (16) Foreign inflation AR(1)
pi_star = rho_pi_star * pi_star(-1) + eps_pi_star;

% (17) Foreign interest rate AR(1)
i_star = rho_i_star * i_star(-1) + eps_i_star;

% ---- Auxiliary Variables ----

% (18) Nominal exchange rate level (cumulative depreciation)
e_level = e_level(-1) + ec;

% (19) Current account definition
ca = y - c;

end;

%% ------------------------------------------------------------------------
%  6. STEADY STATE (all variables = 0 in log-deviations)
%% ------------------------------------------------------------------------
initval;
    c = 0; y = 0; i = 0; pi = 0; piH = 0; piF = 0;
    S = 0; q = 0; mc = 0; a = 0; ec = 0; e_level = 0; ca = 0;
    y_star = 0; pi_star = 0; i_star = 0;
    tau = 0; g = 0; epsH = 0;
end;

steady;
check;

%% ------------------------------------------------------------------------
%  7. SHOCK SPECIFICATION (1% = 0.01 std dev)
%% ------------------------------------------------------------------------
shocks;
    var eps_m;       stderr 0.01;
    var eps_z;       stderr 0.01;
    var eps_tau;     stderr 0.01;
    var eps_H;       stderr 0.01;
    var eps_y_star;  stderr 0.01;
    var eps_pi_star; stderr 0.01;
    var eps_i_star;  stderr 0.01;
end;

%% ------------------------------------------------------------------------
%  8. SIMULATION AND IRF GENERATION
%% ------------------------------------------------------------------------
% Compute IRFs for all shocks (12 quarters)
stoch_simul(order=1, irf=12, nograph);

% Note: Run plot_irfs.m separately to generate publication-quality figures
