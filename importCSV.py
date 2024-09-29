import adsk.core, adsk.fusion, traceback
import io

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        # アクティブなデザイン中の全てのコンポーネントを取得
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # csvファイルを選択する画面を立ち上げる
        # 連番csvの中で一番大きな番号を選択する
        title = 'Import Serialized csv'
        if not design:
            ui.messageBox('No active Fusion design', title)
            return
        dlg = ui.createFileDialog()
        dlg.title = 'Open CSV File'
        dlg.filter = 'csv ファイル (*.csv);;All Files (*.*)'
        if dlg.showOpen() != adsk.core.DialogResults.DialogOK:
            return
        filename = dlg.filename

        # 連番csvファイルのリストを作成
        basename = filename[:-8]
        index_max = filename[-8:-4]
        filetype = filename[-4:]
        filenames = [basename + '{:0=4}'.format(index) + filetype for index in range(0, int(index_max)+1, 1)]

        # アクティブコンポーネント中のルートコンポーネントを取得
        rootComp = design.rootComponent
        # スケッチを作成
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xYConstructionPlane)
        for filename in filenames:
            with io.open(filename, 'r', encoding='utf-8-sig') as f:
                points = adsk.core.ObjectCollection.create()
                line = f.readline()
                data = []
                TE = True   # TE: Trailing Edge
                # 開いたcsvファイルから点を読み込む
                while line:
                    pntStrArr = line.split(',')
                    data = []
                    for pntStr in pntStrArr:
                        try:
                            data.append(float(pntStr))
                        except:
                            break
                    if len(data) >= 3:
                        if TE:
                            point_TE = adsk.core.Point3D.create(data[0], data[1], data[2])
                            points.add(point_TE)
                            TE = False
                        else:
                            point = adsk.core.Point3D.create(data[0], data[1], data[2])
                            points.add(point)
                    line = f.readline()
                # 最後に最初(後縁)の点を追加することで曲線を閉じる
                points.add(point_TE)

            if points.count:
                # スプラインを追加
                sketch.sketchCurves.sketchFittedSplines.add(points)
            else:
                ui.messageBox('No valid points', title)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))