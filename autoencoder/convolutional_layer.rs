/*
 * Author: Charlie Goldstraw
 * Email: cpg205@exeter.ac.uk
 * Date: 14-02-2023
 */

use serde::{Serialize, Deserialize};

/// Calculates the sigmoid of a given input value
fn sigmoid(x: f32) -> f32 {
    1.0 / (1.0 + (-x).exp())
}

/// Defines a `ConvolutionalLayer` structure.
#[derive(Serialize, Deserialize)]
pub struct ConvolutionalLayer {
    input_size: usize,                       // Input size
    input_depth: usize,                      // Input depth
    num_filters: usize,                      // Number of filters
    kernel_size: usize,                      // Kernel size
    output_size: usize,                      // Output size
    stride: usize,                           // Stride
    padding: usize,                          // Padding
    biases: Vec<f32>,                        // Vector of biases
    bias_changes: Vec<f32>,                  // Bias minibatch changes
    kernels: Vec<Vec<Vec<Vec<f32>>>>,        // Kernel values
    kernel_changes: Vec<Vec<Vec<Vec<f32>>>>, // Kernel minibatch changes
    sigmoid: bool,                           // Activation Function
    input: Vec<Vec<Vec<f32>>>,               // Input layer
    pub output: Vec<Vec<Vec<f32>>>,          // Output layer
}

impl ConvolutionalLayer {

    /// Pads a 3D matrix with zeroes.
    fn pad(&mut self, input: Vec<Vec<Vec<f32>>>) -> Vec<Vec<Vec<f32>>> {
        let padded_size = self.input_size + 2 * self.padding;
        let mut padded = vec![vec![vec![0.0; padded_size]; padded_size]; self.input_depth];

        for d in 0..self.input_depth {
            for h in self.padding..(padded_size - self.padding) {
                for w in self.padding..(padded_size - self.padding) {
                    padded[d][h][w] = input[d][h - self.padding][w - self.padding];
                }
            }
        }

        padded
    }

    /// Forward propagates the input data through the Convolutional layer.
    pub fn forward_propagate(&mut self, input: Vec<Vec<Vec<f32>>>) -> Vec<Vec<Vec<f32>>> {
        // Store the input data in a member variable for future reference.
        self.input = input;
        let padded_input = self.pad(self.input.clone());

        // Iterate through each output point in the output matrix.
        for y in 0..self.output_size {
            for x in 0..self.output_size {
                // Calculate the starting point for the convolutional kernel.
                let left = x * self.stride;
                let top = y * self.stride;
                // Iterate through each filter in the network.
                for f in 0..self.num_filters {
                    // Initialize the output value with the bias value for the filter.
                    self.output[f][y][x] = self.biases[f];

                    // Iterate through each input channel.
                    for f_i in 0..self.input_depth {
                        for y_k in 0..self.kernel_size {
                            for x_k in 0..self.kernel_size {
                                // Retrieve the value of the input data at the current location.

                                let val: f32 = padded_input[f_i][top + y_k][left + x_k];

                                // Update the output value with the result of the convolution.
                                self.output[f][y][x] += self.kernels[f][f_i][y_k][x_k] * val;
                            }
                        }
                    }
                }
            }
        }

        for f in 0..self.num_filters {
            for y in 0..self.output_size {
                for x in 0..self.output_size {
                    if self.sigmoid {
                        self.output[f][y][x] = sigmoid(self.output[f][y][x]);
                    } else {
                        self.output[f][y][x] = self.output[f][y][x].max(0.0);
                    }
                }
            }
        }

        self.output.clone()
    }
}
