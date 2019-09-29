import cx_Oracle
from dao.connection_info import *


def deleteTrack(track_name, track_artist):
    connection = cx_Oracle.connect(username, password, databaseName)
    cursor = connection.cursor()

    cursor.callproc("WORK_WITH_TRACKS.DELETE_TRACK", [track_name, track_artist])

    cursor.close()
    connection.close()

    return "Track %s successfully deleted!" %track_name


def addTrack(track_name, track_artist, track_album=None):
    connection = cx_Oracle.connect(username, password, databaseName)
    cursor = connection.cursor()

    if not track_album:
        cursor.callproc("WORK_WITH_TRACKS.ADD_TRACK", [track_name, track_artist])
    else:
        cursor.callproc("WORK_WITH_TRACKS.ADD_TRACK", [track_name, track_artist, track_album])

    cursor.close()
    connection.close()

    return track_name


def addTrackHash(track_hash, track_name, track_artist, track_time_piece):
    connection = cx_Oracle.connect(username, password, databaseName)
    cursor = connection.cursor()

    cursor.callproc("WORK_WITH_TRACKS.ADD_TRACK_HASH", [track_hash, track_name, track_artist, track_time_piece])

    cursor.close()
    connection.close()

    return 0


def getNumberOfTracks():
    connection = cx_Oracle.connect(username, password, databaseName)
    cursor = connection.cursor()

    query = 'SELECT DISTINCT count(*) FROM TRACK_INFO'
    cursor.execute(query)

    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result


def getTrackList(track_name=None, track_artist=None):
    connection = cx_Oracle.connect(username, password, databaseName)
    cursor = connection.cursor()

    if not track_name and not track_artist:
        query = 'SELECT * FROM table(WORK_WITH_TRACKS.GET_TRACK_LIST())'
        cursor.execute(query)
    else:
        query = 'SELECT * FROM table(WORK_WITH_TRACKS.GET_TRACK_LIST(:track_name, :track_artist))'
        cursor.execute(query, track_name=track_name, track_artist=track_artist)

    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result


def getTrackHashList(track_name, track_artist):
    connection = cx_Oracle.connect(username, password, databaseName)
    cursor = connection.cursor()

    query = 'SELECT * FROM table(WORK_WITH_TRACKS.GET_TRACK_HASH_LIST(:track_name, :track_artist)) ORDER BY TRACK_TIME_PIECE'
    cursor.execute(query, track_name=track_name, track_artist=track_artist)

    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result
