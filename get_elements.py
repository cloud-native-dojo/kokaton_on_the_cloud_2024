import os
def files_into_dic(file_name="file-list.txt"):
    """ディレクトリ抜きのファイルのみ取得して辞書に変換"""
    cwd = os.getcwd()
    # file_name = "file-list.txt"
    path = f"{cwd}/{file_name}"

    dic = {}  # 最終的な辞書
    stack = []  # 階層を追跡するスタック

    with open(path, "r", encoding="utf-8") as rf:
        for line in rf:
            # 行を整形
            line = line.rstrip().replace("--", "").replace("`", "|").replace(" ", "")
            if (not line) or (line == "1227directories,9059files"): # ""のような空の要素が出現したので、削除
                continue
            
            depth = line.count("|")  # 現在の行の深さを計算
            stripped_line = line.replace("|", "").strip()  # 縦罫線を削除した文字列

            # 最上位ノード（"."）の処理
            if depth == 0:  # 深さが 0 の場合
                dic[stripped_line] = []  # "." を辞書のキーに設定
                stack = [{"key": stripped_line, "ref": dic[stripped_line]}]  # スタックに登録
                continue

            # 現在のスタックの深さが現在の行の深さ以上なら、親ディレクトリに戻る
            while stack and stack[-1]["key"].count("|") >= depth:
                stack.pop()

            parent = stack[-1]["ref"]  # 現在の親ディレクトリを取得

            # 新しいディレクトリまたはファイルを親ディレクトリに追加
            if depth > stack[-1]["key"].count("|"):  # 新しいディレクトリ
                new_entry = {stripped_line: []}
                parent.append(new_entry)
                stack.append({"key": line, "ref": new_entry[stripped_line]})
            else:  # ファイルの場合
                parent.append(stripped_line)
    return dic
            
            
def get_value(d, key):
    """
    ネストされた辞書から任意のキーに対応する値を取得する関数。
    """
    if isinstance(d, dict):
        for k, v in d.items():
            if k == key:  # キーが見つかった場合
                return v
            if isinstance(v, list):  # リスト内を再帰的に探索
                for item in v:
                    if isinstance(item, dict):
                        result = get_value(item, key)
                        if result is not None:
                            return result
    return None  # 見つからない場合は None を返す


def get_all_elmes(file_name="file-list.txt"):
    cwd = os.getcwd()
    # file_name = "file-list.txt"
    path = f"{cwd}/{file_name}"

    all_elmes = []

    with open(path, "r", encoding="utf-8") as rf:
        for line in rf:
            # 行を整形
            line = line.rstrip().replace("--", "").replace("`", "").replace("|", "").replace(" ", "")
            if (line==".") or (not line) or (line == "1227directories,9059files"): # ""のような空の要素が出現したので、削除
                continue
            all_elmes.append(line)
        return all_elmes 


def collect_deepest_files(data):
    """
    辞書形式の階層データから、最も深い階層にあるファイルを収集する。
    """
    result = []

    def traverse(node):
        """
        辞書やリストの構造を再帰的に解析して、ファイルを収集する。
        """
        if isinstance(node, dict):  # 辞書なら
            for key, value in node.items():
                if isinstance(value, list) and value:  # リストが空でない場合
                    traverse(value)
                else:
                    result.append(key)  # ファイル名としてキーを追加
        elif isinstance(node, list):  # リストなら
            for item in node:
                traverse(item)
        else:
            # ファイル名を直接追加
            result.append(node)

    traverse(data)
    return result