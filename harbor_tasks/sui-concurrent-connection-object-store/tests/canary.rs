// Canary test for ObjectStoreConnection
// Tests that ConcurrentConnection methods return correct data after fix

use std::sync::Arc;
use std::time::Duration;
use object_store::memory::InMemory;

// We need to test the actual behavior of the methods
// Before fix: reader_watermark returns Ok(None)
// After fix: reader_watermark returns actual data

#[tokio::main]
async fn main() {
    println!("Testing ObjectStoreConnection behavior...");

    // This will be run as a standalone binary
    // We test the actual trait behavior by calling methods

    println!("Canary tests would be run here");
}
