use std::env;
use std::fs;
use std::io;
use std::io::prelude::*;

fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();
    let note_dir = format!("{}{}{}", &args[1], "\\", "notes\\");

    for path in fs::read_dir(&note_dir).expect("unable to read note directory") {
        let note = path.expect("unable to read note");
        let file = fs::File::open(note.path())?;
        let mut buf_reader = io::BufReader::new(file);
        let mut content = String::new();
        buf_reader.read_to_string(&mut content).expect("error reading note contents");
        println!("{}", content);
    }
    Ok(())
} 