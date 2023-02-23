/*
 * Author: Charlie Goldstraw
 * Email: cpg205@exeter.ac.uk
 * Date: 14-02-2023
 */

use serde::{Serialize, Deserialize};

/// Defines a `MaxPoolingLayer` structure.
#[derive(Serialize, Deserialize)]
pub struct MaxPoolingLayer {
    input_size: usize,
    input_depth: usize,
    kernel_size: usize,
    output_size: usize,
    stride: usize,
    output: Vec<Vec<Vec<f32>>>,
    highest_index: Vec<Vec<Vec<(usize, usize)>>>,
}

impl MaxPoolingLayer {
    /// Reduces the size of the input by using max pooling.
    pub fn forward_propagate(&mut self, input: Vec<Vec<Vec<f32>>>) -> Vec<Vec<Vec<f32>>> {
        // Loop through each output position in the output volume
        for y in 0..self.output_size {
            for x in 0..self.output_size {
                // Calculate the top-left corner of the receptive field
                let left = x * self.stride;
                let top = y * self.stride;
                for f in 0..self.input_depth {
                    self.output[f][y][x] = -1.0;
                    // Loop through each position in the receptive field and update the output to
                    // the highest value.
                    for y_p in 0..self.kernel_size {
                        for x_p in 0..self.kernel_size {
                            let val: f32 = input[f][top + y_p][left + x_p];
                            if val > self.output[f][y][x] {
                                self.output[f][y][x] = val;

                                // Store the highest index for backpropagation.
                                self.highest_index[f][y][x] = (top + y_p, left + x_p);
                            }
                        }
                    }
                }
            }
        }
        self.output.clone()
    }
}
