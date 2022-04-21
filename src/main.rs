use std::env;
use std::fs;

fn main() {
    let args: Vec<String> = env::args().collect();
    println!("{:?}", args);
    let dir = &args[1];
    let paths = fs::read_dir(&dir).unwrap();

    for path in paths {
        println!("Name: {}", path.unwrap().path().display())
    }
}