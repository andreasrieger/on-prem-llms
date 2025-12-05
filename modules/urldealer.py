def get_slugs_from_url(url):
    parts = url.split('/')
    if len(parts) > 3:
        return '/'.join(parts[3:])
    return ''


def get_base_dir_from_url(url):
    parts = url.split('/')
    if len(parts) > 3:
        return parts[3]
    return ''


def get_filename_from_url(url):
    return url.split('/')[-1]


def enrich_dataframe_with_url_parts(df):
    df['slugs'] = df['url'].apply(get_slugs_from_url)
    df['base_dir'] = df['url'].apply(get_base_dir_from_url)
    df['filename'] = df['url'].apply(get_filename_from_url)
    return df