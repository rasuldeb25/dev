%% Gradient Method with Backtracking on the Rosenbrock Function

% Define the Rosenbrock function: f(x1, x2) = (1-x1)^2 + 100(x2-x1^2)^2
% This is the "valley" function we are trying to minimize.
f = @(x) (1 - x(1)).^2 + 100*(x(2) - x(1).^2).^2;

% Define the analytical gradient (partial derivatives of f with respect to x1 and x2)
% This calculates the steepest slope at any given point x.
g = @(x) [-2*(1 - x(1)) - 400*x(1)*(x(2) - x(1).^2); 
    200*(x(2) - x(1).^2)];

% Set the initial starting coordinates (x1 = -1.2, x2 = 1)
x0 = [-1.2; 1];
% Set the stopping tolerance. The loop ends when the gradient is smaller than this.
epsilon = 1e-3;
% Set the absolute maximum number of iterations to prevent an infinite loop.
maxit = 8000;

% Execute the main optimization function defined at the bottom of this script.
% It returns the optimal point, the function value at that point, total steps, and the full path.
[xopt, fopt, k, xpath] = gradmeth_bt(f, g, x0, epsilon, maxit);

% Print the total number of iterations it took to converge.
fprintf('Num of steps: %d\n', k);

%% Plotting Section
% We only want to visualize the final 130 steps to see the microscopic zig-zag.
n_last = 130;
% Extract all rows (coordinates) but only the last 130 columns from the path history.
path_plot = xpath(:, end-n_last:end);

% Define the precise zoomed-in bounding box for the plot axes.
x_lims = [0.99912, 0.99921];
y_lims = [0.99824, 0.99842];

figure;
% Redefine the function using standard x, y variables specifically for the fcontour tool.
f_plot = @(x,y) (1 - x).^2 + 100.*(y - x.^2).^2;
% Draw the background "elevation map" within our zoomed limits.
% 'logspace' generates 100 lines clustered together to visualize the steepness.
levels = linspace(7e-7, 4e-6, 25);
fcontour(f_plot, [x_lims, y_lims], 'LevelList', levels, 'LineWidth', 0.5);
hold on; % Keep the contour map on screen for the next plotting command.

% Plot the zig-zag path using a solid blue line ('b-').

plot(path_plot(1,:), path_plot(2,:), 'b-');
title('Gradient Method With Backtracking');
xlabel('x_1'); ylabel('x_2');
grid on; % Add a grid for readability.
hold off; % Release the plot so future commands don't overwrite it.

%% Custom Functions Section

% --- Main Gradient Descent Manager ---
function [xopt, fopt, k, xpath] = gradmeth_bt(f, g, x0, epsilon, maxit)
k = 0; % Initialize step counter
x = x0; % Set current position to the starting point
xpath = x; % Initialize the path history array with the starting point

% Continue looping as long as the slope is steeper than epsilon AND we haven't hit the limit
while norm(g(x)) > epsilon && k < maxit
    p = -g(x); % Search direction is strictly opposite to the gradient (downhill)

    % Ask the sub-function to find the best step size (alpha) for this specific move.
    % We pass the standard Armijo parameters: alpha_max=1, c=1e-4, rho=0.5
    alpha = backtracking(f, g, p, x, 1, 1e-4, 0.5); 

    x = x + alpha * p; % Calculate the new position based on direction and step size
    xpath = [xpath, x]; % Append the new coordinates to our path history
    k = k + 1; % Increment the step counter
end

xopt = x; % The final position when the loop breaks is our optimal solution
fopt = f(xopt); % Calculate the actual function value at that optimal spot
end

% --- Backtracking Line Search (Armijo Condition) ---
function alpha = backtracking(f, grad, p, x, alpha_max, c, rho)
% Define default values for the parameters in case they are omitted in the function call
arguments
    f, grad, p, x
    alpha_max = 1
    c = 1e-4
    rho = 0.5
end

alpha = alpha_max; % Always start by attempting a full-size step (alpha = 1)

% The Armijo Condition check:
% While the step doesn't decrease the function value "enough" (based on 'c' and the gradient)
while (f(x + alpha*p) > f(x) + alpha * c * (grad(x)' * p))
    alpha = rho * alpha; % Shrink the step size by multiplying by rho (cutting it in half)
end
% When the loop breaks, we have found an acceptable alpha and return it to the main function
end