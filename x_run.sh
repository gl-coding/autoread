function auto_read(){
    suffix=$1
    #先开启微信阅读，打开相应的书，然后运行这个脚本，截图保存在screenshots目录
    python mouse_tracker.py -o data/$suffix/screenshots
}

function crop() {
    suffix=$1
    #先清空目录，裁剪目录
    rm -rf data/$suffix/cropped
    #再清空分割目录
    rm -rf data/$suffix/split_results
    #再清空ocr目录
    rm -rf data/$suffix/ocr_results

    # 裁剪图片，去掉电脑背景的边框，保留书本的内容
    python batch_crop.py data/$suffix/screenshots data/$suffix/cropped

    # 分割图片，将书本分割为左右两部分
    python image_split.py --batch data/$suffix/cropped data/$suffix/split_results
}

function gen_pdf() {
    suffix=$1
    crop $suffix
    # 识别图片，将左右两部分图片识别为文字，并合并为pdf
    python images_to_pdf.py data/$suffix/split_results
}

function ocr(){
    suffix=$1
    python ocr_tesseract.py data/$suffix/split_results data/$suffix/ocr_results
}

function process_word() {
    #bash x_run.sh word words_6ji/
    arg=$1
    t=$2
    jq '.pre_dir = "data/'$arg'"' llm_utils.json > tmp.json && mv tmp.json llm_utils.json
    if [ "$t" == "multi" ]; then
        python process_100words.py multi
    elif [ "$t" == "single" ]; then
        python process_100words.py single
    elif [ "$t" == "merge" ]; then
        python process_100words.py merge
        python process_100words.py process
    fi
}

function process_article() {
    suffix=$1
    python process_Jobs.py ocr_results_$suffix
}

arg=$1
case $arg in
    "auto")
        auto_read $2
        ;;
    "crop")
        crop $2
        ;;
    "gen")
        gen_pdf $2
        ;;
    "ocr")
        ocr $2
        ;;
    "word")
        process_word $2 $3
        ;;
    "article")
        process_article $2
        ;;
    *)
        echo "Usage: $0 {gen_pdf}"
        ;;
esac