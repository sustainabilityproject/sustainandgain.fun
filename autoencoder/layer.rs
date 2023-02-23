/*
 * Author: Charlie Goldstraw
 * Email: cpg205@exeter.ac.uk
 * Date: 14-02-2023
 */

use crate::convolutional_layer::ConvolutionalLayer;
use crate::fully_connected_layer::FullyConnectedLayer;
use crate::max_pooling_layer::MaxPoolingLayer;
use crate::unmax_pooling_layer::UnMaxPoolingLayer;
use serde::{Serialize, Deserialize};

/// Flattens a 3D vector into a 1D vector.
fn flatten(squares: Vec<Vec<Vec<f32>>>) -> Vec<f32> {
    let mut flat_data: Vec<f32> = vec![];

    // Flatten the input by iterating through each square, then each row, and extending the flat_data vector.
    for square in squares {
        for row in square {
            flat_data.extend(row);
        }
    }

    flat_data
}

/// Represents a layer in a neural network.
#[derive(Serialize, Deserialize)]
pub enum Layer {
    /// A Convolutional Layer
    Conv(ConvolutionalLayer),
    /// A Max Pooling Layer
    Mxpl(MaxPoolingLayer),
    /// A Fully Connected Layer
    Fcl(FullyConnectedLayer),
    /// An Unpooling layer
    Unmxpl(UnMaxPoolingLayer),
}

impl Layer {
    /// Forward propagates input through the layer
    pub fn forward_propagate(&mut self, input: Vec<Vec<Vec<f32>>>) -> Vec<Vec<Vec<f32>>> {
        match self {
            Layer::Conv(a) => a.forward_propagate(input),
            Layer::Mxpl(b) => b.forward_propagate(input),
            Layer::Fcl(c) => c.forward_propagate(flatten(input)),
            Layer::Unmxpl(e) => e.forward_propagate(input),
        }
    }

    /// Returns the output value at a specific index
    pub fn get_output(&mut self, index: (usize, usize, usize)) -> f32 {
        match self {
            Layer::Conv(a) => a.output[index.0][index.1][index.2],
            Layer::Mxpl(_) => panic!("Layer not deconvolutional"),
            Layer::Fcl(_) => panic!("Layer not deconvolutional"),
            Layer::Unmxpl(_) => panic!("Layer not deconvolutional"),
        }
    }
}
