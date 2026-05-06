text = 'McMillan and Kraft inequalities imply that for any uniquely decodable code there exists a prefix code having the same codeword lengths.';

symbols = unique(text);

cell_symbols = num2cell(symbols);

freq = [];
for i = 1:length(symbols)
    freq = [freq, count(text, symbols(i))];
end 

prob_orig = freq / length(text);

%% 
[dict_huff, E_huff] = huffmandict(cell_symbols, prob_orig);

%% 
[prob, sort_idx] = sort(prob_orig, 'descend');

L = ceil(-log2(prob));

n = length(prob);
w = zeros(1, n);
for i = 2:n
    w(i) = sum(prob(1:i-1));
end

int_values = floor((2.^L) .* w);

codes_sorted = cell(n, 1);
for i = 1:n
    codes_sorted{i} = dec2bin(int_values(i), L(i));
end

codes_orig = cell(n, 1);
codes_orig(sort_idx) = codes_sorted;

%% 
final_array = cell(n, 3);

for i = 1:n
    final_array{i, 1} = cell_symbols{i};
    final_array{i, 2} = dict_huff{i, 2};
    final_array{i, 3} = codes_orig{i};
end

%% 
H = -sum(prob_orig .* log2(prob_orig));

Eff_huff = H / (E_huff * log2(2));

E_shan = sum(prob .* L);
Eff_shan = H / (E_shan * log2(2));

%% 
disp('Final Cell Array: [Symbol] | [Huffman Code] | [Shannon Code]');
disp(final_array);

fprintf('--- Efficiencies ---\n');
fprintf('Entropy (H):           %.4f bit/symbol\n', H);
fprintf('Huffman Efficiency:    %.4f (%.2f %%)\n', Eff_huff, Eff_huff * 100);
fprintf('Shannon Efficiency:    %.4f (%.2f %%)\n', Eff_shan, Eff_shan * 100);