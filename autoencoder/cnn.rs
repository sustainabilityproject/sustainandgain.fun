/*
 * Author: Charlie Goldstraw
 * Email: cpg205@exeter.ac.uk
 * Date: 14-02-2023
 */

use crate::IMAGE_SIZE;
use crate::layer::Layer;
use std::fs::File;
use std::io::Read;
use image::RgbImage;
use serde::{Serialize, Deserialize};

/// A struct that represents a Convolutional Neural Network (CNN)
#[derive(Serialize, Deserialize)]
pub struct CNN {
    /// A vector of `Layer` objects representing the layers in the CNN
    layers: Vec<Layer>,
}

impl CNN {
    /// Forward propagates an input matrix through the CNN.
    pub fn forward_propagate(&mut self, input: Vec<Vec<Vec<f32>>>) -> Vec<Vec<Vec<f32>>> {
        let mut output: Vec<Vec<Vec<f32>>> = input;

        // Forward propagate through each layer of the network
        for i in 0..self.layers.len() {
            output = self.layers[i].forward_propagate(output);
        }

        // Flatten and return the output of the final layer
        output
    }

    /// Calculates the cost of the last layer of the network
    pub fn cost(&mut self, image: Vec<Vec<Vec<f32>>>) -> f32 {
        let mut cost: f32 = 0.0;
        let last_index: usize = self.layers.len() - 1;

        // Calculate the error for each output neuron
        for z in 0..3 {
            for y in 0..IMAGE_SIZE {
                for x in 0..IMAGE_SIZE {
                    let output: f32 = self.layers[last_index].get_output((z,y,x));
                    cost += (output - image[z][y][x]).powi(2) / (IMAGE_SIZE * IMAGE_SIZE * 3) as f32;
                }
            }
        }

        cost
    }

    /// Converts the output of the network to an image, storing it in a file named output {i}.
    pub fn generate_image(&mut self) {
        let last_index: usize = self.layers.len() - 1;
        let mut img = RgbImage::new(IMAGE_SIZE as u32, IMAGE_SIZE as u32);

        for y in 0..IMAGE_SIZE {
            for x in 0..IMAGE_SIZE {
                let r = self.layers[last_index].get_output((0, y, x));
                let g = self.layers[last_index].get_output((1, y, x));
                let b = self.layers[last_index].get_output((2, y, x));
                let pixel = image::Rgb([(r * 255.0) as u8, (g * 255.0) as u8, (b * 255.0) as u8]);
                img.put_pixel(x as u32, y as u32, pixel);
            }
        }

        let filename = format!("{}autoencoder/output.png", "./");
        img.save(filename).unwrap();
    }
    
    /// Load the model from a file
    pub fn load_model(filename: &str) -> Result<CNN, std::io::Error> {
        let mut file = File::open(filename)?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;
        let deserialized: CNN = serde_json::from_str(&contents).unwrap();
        Ok(deserialized)
    }
}
