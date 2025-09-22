function gen_pdf() {
    rm -rf cropped
    rm -rf split_results
    #rm -rf ocr_results

    # 裁剪图片，去掉电脑背景的边框，保留书本的内容
    python batch_crop.py

    # 分割图片，将书本分割为左右两部分
    python image_split.py --batch cropped split_results

    # 识别图片，将左右两部分图片识别为文字，并合并为pdf
    python images_to_pdf.py

    mv output/output.pdf ~/Downloads

    open ~/Downloads
}

function auto_read(){
    #先开启微信阅读，打开相应的书，然后运行这个脚本
    python mouse_tracker.py
}

arg=$1
case $arg in
    "gen_pdf")
        gen_pdf
        ;;
    *)
        echo "Usage: $0 {gen_pdf}"
        ;;
esac