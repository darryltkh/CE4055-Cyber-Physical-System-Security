from scipy import stats
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

NO_OF_TRACES = 100
TOTAL_POWER_TRACE_POINTS = 2500
NO_OF_POSSIBLE_KEY_BYTES = 256
NO_OF_BYTES_IN_KEY = 16

SBOX = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
)

def str_to_int(pt):
    byte_list = [pt[i:i+2] for i in range(0,len(pt), 2)]
    return [int(i, 16) for i in byte_list]

def hw(int_no):
    # Write Code to calculate the number of ones in a byte...
    weight = 0
    while int_no:
        weight += 1
        int_no &= int_no - 1
    return weight

def get_power_model(plaintext_byte, no_of_traces = NO_OF_TRACES, Sbox = SBOX, no_of_possible_key_bytes = NO_OF_POSSIBLE_KEY_BYTES):
    power_model_matrix = []
    for k in range(NO_OF_POSSIBLE_KEY_BYTES):
        hamming_weight_of_leaky_sbox_bytes = []
        for i in range(no_of_traces):
            add_round_key = plaintext_byte[i]^k
            sbox_output = Sbox[add_round_key]
            hamming_weight = hw(sbox_output)
            hamming_weight_of_leaky_sbox_bytes.append(hamming_weight)
        power_model_matrix.append(hamming_weight_of_leaky_sbox_bytes)
    return power_model_matrix

def correlate_model_with_actual_trace(power_model_matrix, power_traces, no_of_traces = NO_OF_TRACES, no_of_possible_key_bytes = NO_OF_POSSIBLE_KEY_BYTES, total_power_trace_points = TOTAL_POWER_TRACE_POINTS):
    coeff_per_key_byte = []
    max_coeff_per_key_byte = []
    max_coeff_per_key_byte_column_loc = []

    for j in range(NO_OF_POSSIBLE_KEY_BYTES):
        model_trace = power_model_matrix[j][:no_of_traces]
        coeff_per_column = []

        for k in range(1, TOTAL_POWER_TRACE_POINTS+1):
            column = "Trace " + str(k)
            actual_trace = power_traces[column].tolist()[:no_of_traces]
            coeff, _ = stats.pearsonr(model_trace, actual_trace)
            coeff_per_column.append(coeff)
        
        coeff_per_key_byte.append(coeff_per_column)
        max_coeff_per_key_byte.append(max(coeff_per_column))
        max_coeff_per_key_byte_column_loc.append(np.array(coeff_per_column).argmax()+1)
    
    return coeff_per_key_byte, max_coeff_per_key_byte, max_coeff_per_key_byte_column_loc

# Gather data
collection_data = pd.read_csv('waveform.csv', header=None)
trace_columns = ["Trace " + str(i) for i in range(1,TOTAL_POWER_TRACE_POINTS+1)]
collection_data.columns = ['Plaintext', 'Ciphertext'] + trace_columns

# Divde power trace and plaintexts
power_traces = collection_data.drop(['Plaintext', 'Ciphertext'], axis='columns')
plaintext_data = collection_data['Plaintext']
plaintext_divided_into_bytes = np.array([str_to_int(i) for i in collection_data['Plaintext'].to_numpy()])
plaintext_bytes = pd.DataFrame(plaintext_divided_into_bytes, columns = ["byte_" + str(i) for i in range(16)])

coeff_matrix = []
coeff_matrix_per_key_byte = []
predicted_key_bytes = []
predicted_key_bytes_column_loc = []
predicted_key_bytes_coeff = []
for i in range(NO_OF_BYTES_IN_KEY):
    byte_column = "byte_" + str(i)
    print(byte_column + ":")
    
    # Get pt_byte
    plaintext_byte = plaintext_bytes[byte_column].to_list()
    
    # Get power_model
    power_model_matrix = get_power_model(plaintext_byte)
    
    # Compare with power_trace
    coeff_per_key_byte, max_coeff_per_key_byte, max_coeff_per_key_byte_column_loc = correlate_model_with_actual_trace(power_model_matrix, power_traces)

    coeff_matrix.append(coeff_per_key_byte)
    
    possible_key_byte = np.array(max_coeff_per_key_byte).argmax()
    possible_key_byte_column_loc = max_coeff_per_key_byte_column_loc[possible_key_byte]
    possible_key_byte_coeff = max(max_coeff_per_key_byte)
    
    predicted_key_bytes.append(possible_key_byte)
    predicted_key_bytes_column_loc.append(possible_key_byte_column_loc)
    predicted_key_bytes_coeff.append(possible_key_byte_coeff)
    
    coeff_matrix_per_key_byte.append(max_coeff_per_key_byte)

predicted_key_bytes_hex = [str(hex(i)).lstrip("0x").upper() for i in predicted_key_bytes]
print("The secret key is: {}".format(' '.join(predicted_key_bytes_hex)))


    