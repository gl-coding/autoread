function run_gitbook() {
    # 生成md文件
    rm -rf honkit_docs
    rm -rf /Users/guolei/work/local/gitbook/*
    python organize_responses.py
    # 复制文档到gitbook
    cp -r honkit_docs/* /Users/guolei/work/local/gitbook
    basedir=`pwd`
    cd /Users/guolei/work/local/gitbook
    # 启动gitbook
    killall -9 honkit
    honkit build
    # 等待5秒
    sleep 5
    # 遍历_book目录下的所有html文件
    find _book -name "*.html" -type f | while read file; do
        fullfile=$(pwd)/$file
        bakfile=$fullfile.bak
        echo $fullfile
        python $basedir/file_processor.py $fullfile $bakfile
        mv $bakfile $fullfile
    done
    cd _book
    python -m http.server 4000
    #honkit serve
    # 打开浏览器
    open http://localhost:4000
}

function sync_files() {
    # 复制文档到gitbook
    rm -rf /Users/guolei/work/local/gitbook/chapters
    cp -r honkit_docs/* /Users/guolei/work/local/gitbook
    # 进入gitbook目录
    cd /Users/guolei/work/local/gitbook

    sh upload.sh
}

case $1 in  
    "gitbook")
        run_gitbook
        ;;
    "sync")
        sync_files
        ;;
esac
