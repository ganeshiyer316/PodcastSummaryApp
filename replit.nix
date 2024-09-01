{pkgs}: {
  deps = [
    pkgs.pkg-config
    pkgs.libsndfile
    pkgs.ffmpeg-full
    pkgs.glibcLocales
  ];
}
