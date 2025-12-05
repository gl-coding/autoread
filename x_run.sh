
function auto_read(){
    #先开启微信阅读，打开相应的书，然后运行这个脚本，截图保存在screenshots目录
    python mouse_tracker.py
}

function crop() {
    suffix=$1
    #先清空目录，裁剪目录
    rm -rf cropped_$suffix
    #再清空分割目录
    rm -rf split_results_$suffix
    #再清空ocr目录
    #rm -rf ocr_results

    # 裁剪图片，去掉电脑背景的边框，保留书本的内容
    python batch_crop.py screenshots_$suffix cropped_$suffix

    # 分割图片，将书本分割为左右两部分
    python image_split.py --batch cropped_$suffix split_results_$suffix
}

function gen_pdf() {
    suffix=$1
    crop $suffix
    # 识别图片，将左右两部分图片识别为文字，并合并为pdf
    python images_to_pdf.py split_results_$suffix
}

function ocr(){
    suffix=$1
    python ocr_tesseract.py split_results_$suffix ocr_results_$suffix
}

function process_word() {
    #bash x_run.sh word words_6ji/
    arg=$1
    jq '.pre_dir = "data/'$arg'"' llm_utils.json > tmp.json && mv tmp.json llm_utils.json
    #python process_100words.py multi
    python process_100words.py single
}

function process_article() {
    suffix=$1
    python process_Jobs.py ocr_results_$suffix
}

arg=$1
case $arg in
    "auto")
        auto_read
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
        process_word $2
        ;;
    "article")
        process_article $2
        ;;
    *)
        echo "Usage: $0 {gen_pdf}"
        ;;
esac