use std::env;
use std::fs;
use std::io;
use std::io::prelude::*;
use regex::Regex;

fn handle_import(statement: &str) {
    let is_github_import = Regex::new(r"[a-zA-Z0-9]*/[a-zA-Z0-9]+").unwrap();
    let is_url_import = Regex::new(r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)").unwrap();
    //let is_local_import = Regex::new(r"").unwrap(); we do this later
    if is_github_import.is_match(statement) {
        handle_github_import(statement);
    } else if is_url_import.is_match(statement) {
        handle_url_import(statement);
    } else {
        println!("invalid import: {}", statement)
    }
}

fn handle_github_import(statement: &str) {
    println!("github import: {}", statement)
}
fn handle_url_import(statement: &str) {
    println!("url import: {}", statement)
}

fn main() -> std::io::Result<()> {
    const STATEMENT_PREFIX: &str = "#";
    const STATEMENT_IMPORT: &str = "import";

    let args: Vec<String> = env::args().collect();
    let note_dir = format!("{}{}{}", &args[1], "\\", "notes\\");
    for path_to_note_folder in fs::read_dir(&note_dir)
        .expect("unable to read notes directory") {
        for path_to_note in fs::read_dir(path_to_note_folder?.path())
            .expect("unable to read note directory") {
                let path = path_to_note?.path();
                let ex = path.extension().unwrap().to_str();
                if ex != Some("txt") { continue }

            let file = fs::File::open(&path).expect("unable to open file");
            let buf_reader = io::BufReader::new(file);

            for (_, line) in buf_reader.lines().enumerate() {
                let unwrapped_line = &line.unwrap();
                match &unwrapped_line[0..1] {
                    STATEMENT_PREFIX => { 
                        match &unwrapped_line[1..7] {
                            STATEMENT_IMPORT => { 
                                handle_import(&unwrapped_line)
                            }
                            _ => { }
                        }
                    },
                    _ => {}
                }
            }
            
        }
    }
    Ok(())
} 