/*
 * Author: Charlie Goldstraw
 * Email: cpg205@exeter.ac.uk
 * Date: 15-02-2023
 */

use serde::{Serialize, Deserialize};

/// Defines a `UnMaxPoolingLayer` structure.
#[derive(Serialize, Deserialize)]
pub struct UnMaxPoolingLayer {
    input_size: usize,
    input_depth: usize,
    output_size: usize,
    output: Vec<Vec<Vec<f32>>>,
}

impl UnMaxPoolingLayer {
    /// Expands each input neuron into a 2x2 field of identical values.
    pub fn forward_propagate(&mut self, input: Vec<Vec<Vec<f32>>>) -> Vec<Vec<Vec<f32>>> {
        // Loop through each output position in the output volume
        for y in 0..self.output_size {
            for x in 0..self.output_size {
                let y_i: usize = y / 2;
                let x_i: usize = x / 2;
                for f in 0..self.input_depth {
                    self.output[f][y][x] = input[f][y_i][x_i];
                }
            }
        }
        self.output.clone()
    }
}
