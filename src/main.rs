use std::env;
use std::fs;
use std::io;
use std::io::prelude::*;

fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();
    let note_dir = format!("{}{}{}", &args[1], "\\", "notes\\");
    for path_to_note_folder in fs::read_dir(&note_dir)
        .expect("unable to read notes directory") {
        for path_to_note in fs::read_dir(path_to_note_folder?.path())
            .expect("unable to read note directory") {
                let path = path_to_note?.path();
                let ex = path.extension().unwrap().to_str();
                //if path.is_dir() { continue; }

            let file = fs::File::open(&path).expect("unable to open file");
            let buf_reader = io::BufReader::new(file);
            match ex {
                Some("txt") => { }
                _ => continue
            };
            for (index, line) in buf_reader.lines().enumerate() {
                let line = line.unwrap();
                println!("{}. {}", index + 1, line);
            }
        }
    }
    Ok(())
} 