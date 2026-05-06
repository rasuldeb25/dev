%% 1. Define the Text and Extract Frequencies
% THE RAW DATA
% WHAT IT DOES: We store the exact assignment sentence in a character array.
text = 'McMillan and Kraft inequalities imply that for any uniquely decodable code there exists a prefix code having the same codeword lengths.';

% FINDING THE ALPHABET
% WHAT IT DOES: 'unique' scans the sentence and pulls out exactly one of each character used in alphabetical order.
symbols = unique(text);

% CONVERTING TO A CELL ARRAY
% WHY IT'S NEEDED: The 'huffmandict' function we use later strictly requires the symbols 
% to be in a cell array format, not a standard character array.
cell_symbols = num2cell(symbols);

% CALCULATING FREQUENCIES (YOUR INSTRUCTOR'S EXACT METHOD)
% WHAT IT DOES: Creates an empty array called 'freq'. Then loops through every unique symbol, 
% uses the 'count' function to see how many times it appears in the text, and attaches that number to the array.
freq = [];
for i = 1:length(symbols)
    freq = [freq, count(text, symbols(i))];
end 

% CALCULATING PROBABILITIES
% WHAT IT DOES: Divides the raw counts by the total length of the text to get a decimal percentage.
prob_orig = freq / length(text);

%% 2. Binary Huffman Code
% GENERATING THE HUFFMAN DICTIONARY
% WHAT IT DOES: Uses the built-in function to generate the dictionary. 
% OUTPUTS: 'dict_huff' contains the symbols and their binary codes. 
% 'E_huff' is automatically calculated as the Average Codeword Length.
[dict_huff, E_huff] = huffmandict(cell_symbols, prob_orig);


%% 3. Binary Shannon Code
% SORTING THE PROBABILITIES
% WHAT IT DOES: Shannon coding strictly requires probabilities to be in decreasing order.
% 'sort_idx' is the "memory" of where the symbols originally were before we shuffled them.
[prob, sort_idx] = sort(prob_orig, 'descend');

% CALCULATING SHANNON LENGTHS (L_i)
% WHAT IT DOES: L = ceil(-log2(p)). This dictates exactly how many bits each code will have.
L = ceil(-log2(prob));

% CALCULATING CUMULATIVE PROBABILITIES (w_i) (YOUR INSTRUCTOR'S EXACT LOOP)
% WHAT IT DOES: Creates an array of zeros. Then loops through and adds up all the 
% probabilities that came before the current symbol. The first one remains 0.
n = length(prob);
w = zeros(1, n);
for i = 2:n
    w(i) = sum(prob(1:i-1));
end

% CALCULATING THE DECIMAL INTEGER VALUES
% WHAT IT DOES: This is your instructor's clever mathematical trick. Instead of generating 
% binary manually, it calculates the base-10 integer value of the code using floor(2^L * w).
int_values = floor((2.^L) .* w);

% GENERATING THE BINARY CODEWORDS
% WHAT IT DOES: Creates an empty cell array. Then loops through our integers and uses 'dec2bin' 
% to instantly translate the base-10 numbers into strings of 1s and 0s with length 'L'.
codes_sorted = cell(n, 1);
for i = 1:n
    codes_sorted{i} = dec2bin(int_values(i), L(i));
end

% REALIGNING TO ORIGINAL ORDER
% WHAT IT DOES: Because we sorted the array for Shannon, we need to unsort it so it lines up 
% perfectly with the Huffman dictionary output. We use our 'sort_idx' memory to snap them back.
codes_orig = cell(n, 1);
codes_orig(sort_idx) = codes_sorted;


%% 4. Creating the Final Cell Array for Display
% BUILDING THE 3-COLUMN TABLE
% WHAT IT DOES: Creates an empty cell array with 'n' rows and 3 columns.
final_array = cell(n, 3);

% FILLING THE TABLE
% WHAT IT DOES: Column 1 gets the symbol. Column 2 gets the Huffman code (from dict_huff). 
% Column 3 gets the unsorted Shannon code. 
for i = 1:n
    final_array{i, 1} = cell_symbols{i};
    final_array{i, 2} = dict_huff{i, 2};
    final_array{i, 3} = codes_orig{i};
end


%% 5. Calculating Efficiencies
% THE ENTROPY (H)
% WHAT IT DOES: Calculates the theoretical limit of compression using Shannon's formula.
H = -sum(prob_orig .* log2(prob_orig));

% HUFFMAN EFFICIENCY
% WHAT IT DOES: Calculates efficiency. Your instructor explicitly includes '*log2(2)' in the denominator. 
% Mathematically log2(2) is just 1, but it is written out to strictly follow the formula.
Eff_huff = H / (E_huff * log2(2));

% SHANNON EFFICIENCY
% WHAT IT DOES: Calculates the average length (E_shan) by multiplying probabilities by lengths, 
% then calculates the efficiency using the same formula.
E_shan = sum(prob .* L);
Eff_shan = H / (E_shan * log2(2));


%% 6. Displaying the Results
disp('Final Cell Array: [Symbol] | [Huffman Code] | [Shannon Code]');
disp(final_array);

fprintf('--- Efficiencies ---\n');
fprintf('Entropy (H):           %.4f bit/symbol\n', H);
fprintf('Huffman Efficiency:    %.4f (%.2f %%)\n', Eff_huff, Eff_huff * 100);
fprintf('Shannon Efficiency:    %.4f (%.2f %%)\n', Eff_shan, Eff_shan * 100);
%% 7. Extra: Prefix Code Verification
disp('==================================================');
disp('EXTRA: PREFIX CODE VERIFICATION');
disp('==================================================');

% We start by assuming both are perfect prefix codes (true).
% If we find even one violation, we will switch these to 'false'.
is_huff_valid = true;
is_shan_valid = true;

% DOUBLE LOOP: Compare every letter 'i' against every other letter 'j'
for i = 1:n
    for j = 1:n

        % We only check if i and j are different letters (don't compare 'A' to 'A')
        if i ~= j

            % --- 1. CHECKING HUFFMAN (Numeric Arrays) ---
            code_huff_i = final_array{i, 2};
            code_huff_j = final_array{j, 2};
            len_hj = length(code_huff_j);

            % If code 'i' is longer, check if its first parts match code 'j' exactly
            if length(code_huff_i) >= len_hj
                if isequal(code_huff_i(1:len_hj), code_huff_j)
                    is_huff_valid = false; % Violation found!
                end
            end

            % --- 2. CHECKING SHANNON (Character Strings) ---
            code_shan_i = final_array{i, 3};
            code_shan_j = final_array{j, 3};

            % MATLAB has a built-in function to check if one string starts with another
            if startsWith(code_shan_i, code_shan_j)
                is_shan_valid = false; % Violation found!
            end

        end
    end
end

% --- DISPLAY THE FINAL VERDICT ---
if is_huff_valid
    disp('Huffman Code: VERIFIED (No code is a prefix of another)');
else
    disp('Huffman Code: FAILED (Prefix rule violation detected!)');
end

if is_shan_valid
    disp('Shannon Code: VERIFIED (No code is a prefix of another)');
else
    disp('Shannon Code: FAILED (Prefix rule violation detected!)');
end
disp('==================================================');