use std::env;
use std::fs;
use std::io;
use std::io::prelude::*;
use regex::Regex;
use std::cmp::min;
use std::fs::{File};
use std::io::{Seek, Write};
use reqwest::Client;
use indicatif::{ProgressBar, ProgressStyle};
use futures_util::StreamExt;

fn main() -> std::io::Result<()> {
    const STATEMENT_PREFIX: &str = "#";
    const STATEMENT_IMPORT: &str = "import ";

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
                        match &unwrapped_line[1..8] {
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

fn handle_import(statement: &str) {
    let is_github_import = Regex::new(r"[a-zA-Z0-9]*/[a-zA-Z0-9]+").unwrap();
    let is_url_import = Regex::new(r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)").unwrap();
    //let is_local_import = Regex::new(r"").unwrap(); we do this later
    if is_url_import.is_match(statement) {
        println!("{:?}",statement);
        handle_url_import(is_url_import.captures(&statement).unwrap().get(0).unwrap().as_str());
    } else if is_github_import.is_match(statement) {
        //println!("{:?}",is_github_import.captures(&statement).unwrap().get(0).unwrap().as_str())
        //handle_github_import(statement);
    } else {
        println!("invalid import: {}", statement)
    }
}

fn handle_github_import(github_iden: &str) {
    println!("github import: {}", github_iden);
    //download_file_url(url: &str, packagename: &str)
}
fn handle_url_import(url: &str) {
    println!("url import: {}", url);
    download_file_url(url, "test.bin")
}

#[tokio::main]
async fn download_file_url(url: &str, packagename: &str) {
    download_file(&Client::new(), url, packagename).await.unwrap();
}

pub async fn download_file(client: &Client, url: &str, path: &str) -> Result<(), String> {
    let res = client
        .get(url)
        .send()
        .await
        .or(Err(format!("Failed to GET from '{}'", &url)))?;
    let total_size = res
        .content_length()
        .ok_or(format!("Failed to get content length from '{}'", &url))?;

    let pb = ProgressBar::new(total_size);
    pb.set_style(ProgressStyle::default_bar()
        .template("{msg}\n{spinner:.green} [{elapsed_precise}] [{wide_bar:.white/blue}] {bytes}/{total_bytes} ({bytes_per_sec}, {eta})")
        .progress_chars("#"));
    pb.set_message("Downloading");

    let mut file;
    let mut downloaded: u64 = 0;
    let mut stream = res.bytes_stream();
    
    println!("Seeking in file.");
    if std::path::Path::new(path).exists() {
        println!("File exists. Resuming.");
        file = std::fs::OpenOptions::new()
            .read(true)
            .append(true)
            .open(path)
            .unwrap();

        let file_size = std::fs::metadata(path).unwrap().len();
        file.seek(std::io::SeekFrom::Start(file_size)).unwrap();
        downloaded = file_size;

    } else {
        println!("Fresh file..");
        file = File::create(path).or(Err(format!("Failed to create file '{}'", path)))?;
    }

    println!("Commencing transfer");
    while let Some(item) = stream.next().await {
        let chunk = item.or(Err(format!("Error while downloading file")))?;
        file.write(&chunk)
            .or(Err(format!("Error while writing to file")))?;
        let new = min(downloaded + (chunk.len() as u64), total_size);
        downloaded = new;
        pb.set_position(new);
    }

    //pb.finish_with_message(&format!("Downloaded {} to {}", url, path));
    return Ok(());
}