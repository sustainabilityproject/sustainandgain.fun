use pyo3::prelude::*;

/*
 * Author: Charlie Goldstraw
 * Email: cpg205@exeter.ac.uk
 * Date: 13-02-2023
 */

use crate::cnn::CNN;
use image::{io::Reader as ImageReader, GenericImageView, DynamicImage};

const IMAGE_SIZE: usize = 32;

pub mod cnn;
pub mod convolutional_layer;
pub mod fully_connected_layer;
pub mod layer;
pub mod max_pooling_layer;
pub mod unmax_pooling_layer;

/// Converts a Vec<u8> image to two Vec<Vec<Vec<f32>>> structures representing
/// an unchanged and a normalized image for the autoencoder.
fn format_image(input: DynamicImage) -> (Vec<Vec<Vec<f32>>>,Vec<Vec<Vec<f32>>>) {
    let mut raw_img = vec![vec![vec![0.0; IMAGE_SIZE]; IMAGE_SIZE]; 3];
    let mut normalized_image = vec![vec![vec![0.0; IMAGE_SIZE]; IMAGE_SIZE]; 3];
    for x in 0..IMAGE_SIZE {
        for y in 0..IMAGE_SIZE {
            raw_img[0][y][x] = input.get_pixel(x as u32, y as u32)[0] as f32 / 255.0;
            raw_img[1][y][x] = input.get_pixel(x as u32, y as u32)[1] as f32 / 255.0;
            raw_img[2][y][x] = input.get_pixel(x as u32, y as u32)[2] as f32 / 255.0;

            normalized_image[0][y][x] = input.get_pixel(x as u32, y as u32)[0] as f32;
            normalized_image[1][y][x] = input.get_pixel(x as u32, y as u32)[1] as f32;
            normalized_image[2][y][x] = input.get_pixel(x as u32, y as u32)[2] as f32;
        }
    }

    for i in 0..3 {
        // Calculate the mean and standard deviation of the channel
        let mean = normalized_image[i].iter().flatten().sum::<f32>() / (IMAGE_SIZE * IMAGE_SIZE) as f32;
        let variance = normalized_image[i].iter().flatten().map(|&x| (x - mean).powi(2)).sum::<f32>() / (IMAGE_SIZE * IMAGE_SIZE) as f32;
        let std_deviation = variance.sqrt();
        // Normalize the channel by subtracting the mean and dividing by the standard deviation
        for row in &mut normalized_image[i] {
            for pixel in row {
                *pixel = (*pixel - mean) / std_deviation;
            }
        }
    }
    
    (normalized_image, raw_img)
}

#[pyfunction]
pub fn mug_confidence(path_to_img: String) -> f32 {
    let image = match ImageReader::open(path_to_img) {
        Ok(reader) => match reader.decode() {
            Ok(image) => image,
            Err(error) => panic!("Failed to decode image: {}", error),
        },
        Err(error) => panic!("Failed to open image: {}", error),
    };

    let formatted_image = format_image(image);
    let mut cnn: CNN = CNN::load_model("./autoencoder/final_model.json").unwrap();
    cnn.forward_propagate(formatted_image.0);
    cnn.cost(formatted_image.1)
}

/// A Python module implemented in Rust.
#[pymodule]
fn autoencoder(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(mug_confidence, m)?)?;
    Ok(())
}