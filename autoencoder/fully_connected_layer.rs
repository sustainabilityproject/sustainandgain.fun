/*
 * Author: Charlie Goldstraw
 * Email: cpg205@exeter.ac.uk
 * Date: 14-02-2023
 */

use serde::{Serialize, Deserialize};

/// Defines a `FullyConnectedLayer` structure.
#[derive(Serialize, Deserialize)]
pub struct FullyConnectedLayer {
    input_size: usize,              // Number of neurons in input layer.
    input_width: usize,             // Width of input matrix
    input_depth: usize,             // Number of input channels
    output_width: usize,            // Width of output
    output_depth: usize,            // Depth of output
    output_size: usize,             // Number of neurons in output layer.
    weights: Vec<Vec<f32>>,         // Weights of the layer
    weight_changes: Vec<Vec<f32>>,  // Bias minibatch changes
    biases: Vec<f32>,               // Biases of the layer
    bias_changes: Vec<f32>,         // Bias minibatch changes
    input: Vec<f32>,                // Input vector
    output: Vec<f32>,               // Output vector
}

impl FullyConnectedLayer {
    /// Calculates the output layer by forward propagating the input layer.
    pub fn forward_propagate(&mut self, input: Vec<f32>) -> Vec<Vec<Vec<f32>>> {
        // Store the input vector for use in backpropgation.
        self.input = input.clone();
        for j in 0..self.output_size {
            self.output[j] = self.biases[j];
            // Loop through each neuron in the input layer and calculate the weighted sum
            for i in 0..self.input_size {
                self.output[j] += input[i] * self.weights[i][j];
            }
            // Apply the sigmoid activation function to the output value
            // self.output[j] = sigmoid(self.output[j]);
            self.output[j] = self.output[j].max(0.0);
        }
        
        // Rearrange the error vector into a 3D structure for the next layer
        let mut output_3d: Vec<Vec<Vec<f32>>> = vec![vec![vec![]; self.output_width]; self.output_depth];
        for i in 0..self.output_depth {
            for j in 0..self.output_width {
                for k in 0..self.output_width {
                    let index: usize = i * self.output_width.pow(2) + j * self.output_width + k;
                    output_3d[i][j].push(self.output[index]);
                }
            }
        }

        output_3d
    }
}
