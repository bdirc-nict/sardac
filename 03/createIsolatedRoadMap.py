# coding: utf-8
#==================================================================================
# SAR Data Analysis Program
#
# File name		: createIsolatedRoadMap.py
# Creation date	: May 20, 2019
# Python version: 3.6
# License   	: GPL v2
# Copyright (c) 2019 National Institute of Information and CommunicationsTechnology
#==================================================================================

import sys
import shapefile
import time
import router
import csv
import argparse

cutNodes = []
newWayId = 0


def checkCollision(poly, node1, node2):
    """
    1つのグリッドと1つのconnectionの交差判定
    :param poly: グリッド四隅の頂点座標タプルのリスト
    :param node1: connectionの一端ノード
    :param node2: connectionの一端ノード
    """
    
    points = poly.points
    for i in range(len(points) - 1):
        point1 = points[i]
        point2 = points[i + 1]
        lat1 = float(node1.lat) * 100000
        lat2 = float(node2.lat) * 100000
        lat3 = point1[1] * 100000
        lat4 = point2[1] * 100000
        lon1 = float(node1.lon) * 100000
        lon2 = float(node2.lon) * 100000
        lon3 = point1[0] * 100000
        lon4 = point2[0] * 100000

        a = (lat2 - lat1) * (lon3 - lon1) + (lat1 - lat3) * (lon2 - lon1)
        b = (lat2 - lat1) * (lon4 - lon1) + (lat1 - lat4) * (lon2 - lon1)

        c = (lat4 - lat3) * (lon1 - lon3) + (lat3 - lat1) * (lon4 - lon3)
        d = (lat4 - lat3) * (lon2 - lon3) + (lat3 - lat2) * (lon4 - lon3)
        if (a * b <= 0 and c * d <= 0):
            return True
    return False


def divideConnection(cutter):
    """
    wayを引数cutterの位置で2つに分割する
    :param cutter: 寸断したいconnection型インスタンス
    """
    global newWayId
    newWayId1 = newWayId + 1
    newWayId2 = newWayId + 2
    newWayId += 2

    preNode = cutter.node1
    nowNode = cutter.node2

    while(True):
        connections = [x for x in nowNode.connections if x.wayId == cutter.wayId and x.getOtherNode(nowNode) != preNode and x != cutter]
        if(len(connections) == 0):
            break
        cursor = connections[0]
        cursor.wayId = newWayId1
        preNode = nowNode
        nowNode = cursor.getOtherNode(preNode)

    preNode = cutter.node2
    nowNode = cutter.node1

    while(True):
        connections = [x for x in nowNode.connections if x.wayId == cutter.wayId and x.getOtherNode(nowNode) != preNode and x != cutter]
        if(len(connections) == 0):
            break
        cursor = connections[0]
        cursor.wayId = newWayId2
        preNode = nowNode
        nowNode = cursor.getOtherNode(preNode)

    cutter.node1.connections.remove(cutter)
    cutter.node2.connections.remove(cutter)

    cutNodes.extend([cutter.node1, cutter.node2])


def checkIntersection(db, grid):
    """
    あるグリッド領域について、領域を横切るconnectionがdb内に存在するかを確認する
    :param db: routingDb型変数
    :param grid: グリッド四隅の頂点座標タプルのリスト
    """
    myVisitorId = int(time.time() * 1000)
    for node in db.listOfNodes.values():
        for connection in node.connections:
            if (connection.isCut or connection.lastVisitorId == myVisitorId):
                continue

            if (checkCollision(grid, connection.node1, connection.node2)):
                divideConnection(connection)
                connection.isCut = True

            connection.lastVisitorId = myVisitorId


def cutConnections(db, nodeIndices, ignoreNodePairs):
    """
    db内のconnectionのうち、両端ノードがいずれもnodeIndicesに含まれるものをカットする
    :param db:routingDb型変数
    :param nodeIndices:
    :param ignoreNodePairs:カットしたくないノードidのペアの集合
    """
    
    for node in db.listOfNodes.values():
        connectionsToCut = [x for x in node.connections if int(x.node1.id) in nodeIndices and int(x.node2.id) in nodeIndices]

        for cutter in connectionsToCut:
            isIgnore = False
            for pair in ignoreNodePairs:
                if ({int(cutter.node1.id), int(cutter.node2.id)} <= {pair[0], pair[1]}):
                    isIgnore = True # 注目するconnectionの両端ノードが、無視したいノードペアと同じ組み合わせならば、切断しない
                    break

            if (not isIgnore):
                divideConnection(cutter)


def outputHighwayLineShape(outputFilePath, db, isIgnoreIsolated = False):
    """
    highwayをshp出力する
    :param outputFilePath:出力ファイル名
    :param db:routingDb型変数
    """
    print('<--- highwayのshp出力 --->')
    lineCount = 0
    nodeCount = 0

    myVisitorId = int(time.time() * 1000)
    writer = shapefile.Writer(outputFilePath, encoding = 'cp932')
    writer.field('hoge', 'N')

    for node in db.listOfNodes.values():
        for connection in node.connections:
            if (connection.lastVisitorId == myVisitorId):
                continue

            nowNode = node
            nodeSequence = [[float(node.lon), float(node.lat)]]
            connection.lastVisitorId = myVisitorId
            nowConnection = connection
            while (True):
                nextNode = nowConnection.getOtherNode(nowNode)
                nowConnection.lastVisitorId = myVisitorId
                if not (isIgnoreIsolated and nowConnection.isIsolated):
                    nodeSequence.append([float(nextNode.lon), float(nextNode.lat)])
                    nodeCount += 1

                nextConnection = [x for x in nextNode.connections if x.wayId == nowConnection.wayId and x.lastVisitorId != myVisitorId]
                if (len(nextConnection) < 1):
                    break
                nowNode = nextNode
                nowConnection = nextConnection[0]

            writer.line([nodeSequence])
            writer.record(myVisitorId)
            lineCount += 1

    writer.close()
    print(outputFilePath + ' visitorId:' + str(myVisitorId))
    print('lineCount:' + str(lineCount) + ' nodeCount:' + str(nodeCount))


def findIsolatedNodes(db, initialNodes, minLon, minLat, maxLon, maxLat,ot_isolatedNodes):
    """
    孤立した道路NWノードを探索し、shp出力する
    :param db: routingDb型変数
    :param initialNodes: 探索の起点にしたいnodeリスト = 寸断したconnectionの両端ノード集合
    :param minLon: 孤立判定座標(最小経度)
    :param minLat: 孤立判定座標(最小緯度)
    :param maxLon: 孤立判定座標(最大経度)
    :param maxLat: 孤立判定座標(最大緯度)
    :param ot_isolatedNodes: 孤立道路ＮＷノード名
    """
    
    print('<--- 孤立ノード探査開始 --->')
    writer = shapefile.Writer(ot_isolatedNodes, encoding='cp932')
    writer.field('id', 'N')
    myVisitorId = int(time.time() * 1000)

    finishedNodeCount = 0
    isolatedNodeCount = 0

    for node in initialNodes:
        nowVisitorId = myVisitorId + finishedNodeCount + 1
        visitedNodes = []
        nodesToVisit = []
        visitedConnections = []
        isIsolated = False

        cursor = node   # cursorは注目しているノード
        cursor.lastVisitorId = nowVisitorId

        while (True):
            lat = float(cursor.lat)
            lon = float(cursor.lon)
            if (lat <= minLat or lat >= maxLat or lon <= minLon or lon >= maxLon):
                break   # 注目ノードが領域端部に到達したら探査終了

            isReachedVisitedNode = False
            for connection in cursor.connections:
                if (connection.lastVisitorId == nowVisitorId):
                    continue
                visitedConnections.append(connection)
                connection.lastVisitorId = nowVisitorId
                nextNode = connection.getOtherNode(cursor)
                if (nextNode.lastVisitorId == nowVisitorId):
                    continue   # 経路がループしているならば、次のイテレーションへ
                if (nextNode.lastVisitorId == myVisitorId) :
                    isReachedVisitedNode = True # 隣のノードがすでに探査済みならば、イテレーションを抜ける
                    isIsolated = nextNode.isIsolated
                    break

                nodesToVisit.append(nextNode)

            visitedNodes.append(cursor)

            if (isReachedVisitedNode):
                break

            if (len(nodesToVisit) == 0):
                isIsolated = True   # 到達可能なノードを探査し尽くしたならば探査終了
                break

            cursor = nodesToVisit.pop(0)
            cursor.lastVisitorId = myVisitorId

        if (isIsolated):
            for node in visitedNodes:
                writer.point(float(node.lon), float(node.lat))
                writer.record(int(node.id))
                node.lastVisitorId = myVisitorId
                node.isIsolated = True
                isolatedNodeCount += 1
            for connection in visitedConnections:
                connection.isIsolated = True
        else:
            for node in visitedNodes:
                node.lastVisitorId = myVisitorId

        finishedNodeCount += 1
        if (finishedNodeCount % 10 == 0):
            print('finished:' + str(finishedNodeCount) + ' isolated:' + str(isolatedNodeCount))

    writer.close()



if __name__ == "__main__":
    """
    土砂崩れ等により孤立した道路を探索しshapefileとして出力
    """

    parser = argparse.ArgumentParser(description="createIsolatedRoadMap")
    
    parser.add_argument("in_file_osm")
    parser.add_argument("in_file_grid")
    parser.add_argument("ot_file_allHighway")
    parser.add_argument("ot_file_cutNodes")
    parser.add_argument("ot_file_cutHighway")
    parser.add_argument("ot_file_notIsolatedHighway")
    parser.add_argument("ot_file_allNodes")
    parser.add_argument("ot_file_isolatedNodes")
    
    
    args = parser.parse_args()
    
    ### osmファイルを読み込み、道路ネットワークをメモリ上にロードする
    ### way要素のうちhighwayタグが付いているものだけ抽出する
    db = router.routingDb()
    print(router.readDb(open(args.in_file_osm, "r", encoding="utf-8"), db))
    db.cleanUp()

    ### .shp出力
    ### 読み込んだHighway
    outputHighwayLineShape(args.ot_file_allHighway, db)

    cutNodes = []
    newWayId = int(time.time() * 1000000)

    ### connectionの寸断処理

    ### グリッドのshapefileと道路NWのconnectionとの衝突判定
    source = shapefile.Reader(args.in_file_grid, encoding = 'cp932')
    checkedGridCount = 0
    for src in source.iterShapeRecords():
        checkIntersection(db, src.shape)
        checkedGridCount += 1
        if(checkedGridCount % 10 == 0):
            print('checked ' + str(checkedGridCount) + ' grids, and detected ' + str(len(cutNodes)) + 'cut nodes.')
    ###

    ### グリッドによって寸断されたconnection両端のノードid集合がすでにある場合(csv読み込み)
    #nodeIndices = []
    #ignoreNodePairs = []
    #with open('data/cutNodeIndices.csv', 'r') as f:
    #    reader = csv.reader(f)
    #    for row in reader:
    #        nodeIndices.append(int(row[0]))

    #try:
    #    with open('data/ignoreNodesPairs.csv', 'r') as f:
    #        reader = csv.reader(f)
    #        for row in reader:
    #            ignoreNodePairs.append((int(row[0]), int(row[1])))
    #except FileNotFoundError:
    #    ignoreNodePairs = []

    #cutConnections(db, nodeIndices, ignoreNodePairs)
    ###

    ### 孤立した道路NWノードの探索
    findIsolatedNodes(db, cutNodes, 130.9677, 32.8696, 131.0403, 32.9257,args.ot_file_isolatedNodes)

    ### .shp出力
    ### グリッドによって寸断されたconnection両端のノード
    writer = shapefile.Writer(args.ot_file_cutNodes, encoding = 'cp932')
    writer.field('id', 'N')

    for node in cutNodes:
        writer.point(float(node.lon), float(node.lat))
        writer.record(int(node.id))

    writer.close()

    ### .shp出力
    ### 寸断後のhighway
    outputHighwayLineShape(args.ot_file_cutHighway, db)

    ### .shp出力
    ### 孤立していないhighway
    outputHighwayLineShape(args.ot_file_notIsolatedHighway, db, True)

    ### .shp出力
    ### 読み込んだ全ノード
    writer = shapefile.Writer(args.ot_file_allNodes, encoding = 'cp932')
    writer.field('id', 'N')

    for node in db.listOfNodes.values():
        writer.point(float(node.lon), float(node.lat))
        writer.record(int(node.id))

    writer.close()
    
    exit(0)
