syms t s a omega z

f_unit_step = heaviside(t);

f_0 = 1*t^0;
f_1 = t;
f_2 = t^2;

F_unit_step = laplace(f_unit_step);
F_0 = laplace(f_0);
F_1 = laplace(f_1);
F_2 = laplace(f_2);

%% 
f_decaying_exp = exp(-a*t);
f_simple_periodic = exp(1i*omega*t); 
f_cos = cos(omega*t);

F_decaying_exp = laplace(f_decaying_exp);
F_simple_periodic = laplace(f_simple_periodic);
F_cos = laplace(f_cos);

%% 
f_inv_0 = ilaplace(F_0, t);
f_inv_1 = ilaplace(F_1);
f_inv_2 = ilaplace(F_2);
f_inv_decay = ilaplace(F_decaying_exp);
f_inv_periodic = ilaplace(F_simple_periodic);
f_inv_cos = ilaplace(F_cos);

%% 
    syms s X x(t)
    eqn = diff(x, t, 2) + 3*diff(x, t, 1) + 2*x == t;
    L_eqn = laplace(eqn, t, s);
    L_eqn = subs(L_eqn, laplace(x(t), t, s), X);
    L_eqn = subs(L_eqn, [x(0), subs(diff(x(t), t), t, 0)], [0, -2]);
    X_sol = solve(L_eqn, X);
    x_t = ilaplace(X_sol, s, t);
    x_t = simplify(x_t)

%% Disp(function)
syms X x(t) s

eqn = diff(x, t, 2) + 3*diff(x, t, 1) + 2*x == t;
disp('STEP 1');
disp(eqn);
fprintf('\n');


L_eqn = laplace(eqn, t, s);
disp('STEP 2:');
disp(L_eqn);
fprintf('\n');


disp('Table:');
disp(' L{ x(t) }   = X(s)');
disp(' L{ x''(t) }  = s*X(s) - x(0)');
disp(' L{ x''''(t) } = s^2*X(s) - s*x(0) - x''(0)');
disp(' L{ t }      = 1/s^2');
fprintf('\n');


L_eqn = subs(L_eqn, laplace(x(t), t, s), X);
disp('STEP 3:');
disp(L_eqn);
fprintf('\n');


L_eqn = subs(L_eqn, [x(0), subs(diff(x(t), t), t, 0)], [0, -2]);
disp('STEP 4:');
disp(L_eqn);
fprintf('\n');


X_sol = solve(L_eqn, X);
disp('STEP 5:');
disp(X_sol);
fprintf('\n');


x_t = ilaplace(X_sol, s, t);
x_t = simplify(x_t);

disp('STEP 6:');
pretty(x_t)