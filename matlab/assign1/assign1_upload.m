%% Gradient Method with Backtracking on the Rosenbrock Function

f = @(x) (1 - x(1)).^2 + 100*(x(2) - x(1).^2).^2;
g = @(x) [-2*(1 - x(1)) - 400*x(1)*(x(2) - x(1).^2); 
           200*(x(2) - x(1).^2)];

x0 = [-1.2; 1];
epsilon = 1e-3;
maxit = 8000;

[xopt, fopt, k, xpath] = gradmeth_bt(f, g, x0, epsilon, maxit);
 
fprintf('Num of steps: %d\n', k);
%%
n_last = 130;
path_plot = xpath(:, end-n_last:end);

x_lims = [0.99912, 0.99921];
y_lims = [0.99824, 0.99842];

figure;
f_plot = @(x,y) (1 - x).^2 + 100.*(y - x.^2).^2;
levels = linspace(7e-7, 4e-6, 25);
fcontour(f_plot, [x_lims, y_lims], 'LevelList', levels, 'LineWidth', 0.5);
hold on;

plot(path_plot(1,:), path_plot(2,:), 'b-');
title('Gradient Method With Backtracking');
xlabel('x_1'); ylabel('x_2');
grid on;
hold off;
%%
function [xopt, fopt, k, xpath] = gradmeth_bt(f, g, x0, epsilon, maxit)
    k = 0;
    x = x0;
    xpath = x;
    while norm(g(x)) > epsilon && k < maxit
        p = -g(x);
        alpha = backtracking(f, g, p, x, 1, 1e-4, 0.5); 
        x = x + alpha * p;
        xpath = [xpath, x];
        k = k + 1;
    end
    xopt = x;
    fopt = f(xopt);
end
    
function alpha = backtracking(f, grad, p, x, alpha_max, c, rho)
    arguments
        f, grad, p, x
        alpha_max = 1
        c = 1e-4
        rho = 0.5
    end
    alpha = alpha_max;

    while (f(x + alpha*p) > f(x) + alpha * c * (grad(x)' * p))
        alpha = rho * alpha;
    end
end