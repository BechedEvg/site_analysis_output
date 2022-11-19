import json
import cloudscraper


class JsonRW:

    def json_write(self, name, in_dict):
        with open(f'{name}.json', 'w') as outfile:
            json.dump(in_dict, outfile, indent=4, ensure_ascii=False)

    def json_read(self, name):
        with open(f'{name}.json', 'r') as infile:
            return json.load(infile)


def check_amount(google_dict, check_site_dict):
    sitemap = check_site_dict["sitemap"]
    google_amount = len(google_dict["dict_page"])
    sitemap_amount = len(check_site_dict["page_list"])
    if sitemap!= "not_found":
        amount_result = sitemap_amount - google_amount
        if amount_result > 0:
            amount_result = f"there are {amount_result} more links in the sitemap than in Google. {sitemap_amount} pages found"
        elif amount_result < 0:
            amount_result = f"google has more links on {amount_result * -1} than on the sitemap. {google_amount} pages found"
        else:
            amount_result = "the number of links in the sitemap and Google matches."
        return amount_result
    else:
        return f"sitemap not found. {google_amount} pages found"


def get_url_status_cod(url):
    scraper = cloudscraper.create_scraper()
    try:
        return scraper.get(url).status_code
    except:
        return "no_connection"


def comparison_len_title_or_descriptions(google_dict, check_site_dict, list_page_status_code_200, tag):
    pages_dict = check_site_dict["page_list"]
    google_page_dict = google_dict["dict_page"]
    list_result_title = {}
    for page in pages_dict:
        if page in google_page_dict and page in list_page_status_code_200:
            len_tag_site = len(check_site_dict["page_list"][page]["page_content"][tag])
            len_title_google = google_page_dict[page]["len_title_desktop"]
            if len_tag_site != "not_found":
                len_tag = len_tag_site - len_title_google
                if len_tag > 0:
                    len_tag = f"site {tag} is {len_tag} more than google {tag}"
                elif len_tag < 0:
                    len_tag = f"google {tag} is {len_tag * -1} more than site {tag}"
                else:
                    len_tag = f"{tag}s are equal"
                list_result_title[page] = {
                    f"len_{tag}_site": len_tag_site,
                    f"len_{tag}_google": len_title_google,
                    "comparison": len_tag
                }
    return list_result_title


def check_empty_title_or_description(check_site_dict, list_page_status_code_200, tag):
    result_list = []
    for page in list_page_status_code_200:
        if check_site_dict["page_list"][page]["page_content"][tag] == "not_found":
            result_list.append(page)
    return result_list


def check_h1(check_site_dict, list_page_status_code_200):
    result_list = []
    for page in list_page_status_code_200:
        h1_count = check_site_dict["page_list"][page]["page_content"]["list_tag"]["h1"]["count"]
        if h1_count > 1:
            result_list.append(page)
    return result_list


def check_page_status(check_site_dict):
    result_dict = {"3xx": {},
                   "4xx": {},
                   "5xx": {}
                   }
    for page in check_site_dict["page_list"]:
        status_code = check_site_dict["page_list"][page]["status_code"]
        if status_code // 100 == 3:
            try:
                result_dict["3xx"][status_code]["count"] += 1
                result_dict["3xx"][status_code]["list_page"].append(page)
            except:
                result_dict["3xx"][status_code] = {"count": 1, "list_page": []}
        if status_code // 100 == 4:
            try:
                result_dict["4xx"][status_code]["count"] += 1
                result_dict["4xx"][status_code]["list_page"].append(page)
            except:
                result_dict["4xx"][status_code] = {"count": 1, "list_page": []}
        if status_code // 100 == 5:
            try:
                result_dict["5xx"][status_code]["count"] += 1
                result_dict["5xx"][status_code]["list_page"].append(page)
            except:
                result_dict["5xx"][status_code] = {"count": 1, "list_page": []}
    return result_dict


def check_missing_canonical(check_site_dict, list_page_status_code_200):
    list_page_empty_canonical = []
    for page in list_page_status_code_200:
        if check_site_dict["page_list"][page]["page_content"]["canonical"] == "not_found":
            list_page_empty_canonical.append(page)
    return list_page_empty_canonical


# check h tag structure
def check_h_tag_structure(check_site_dict, list_page_status_code_200):
    list_page_result = []
    for page in list_page_status_code_200:
        list_tag = check_site_dict["page_list"][page]["page_content"]["list_tag"]["list_tag"]
        if len(list_tag) > 1 and sorted(list_tag) != list_tag:
            list_page_result.append(page)
    return list_page_result


# check if the image has an "alt" and matches the title
def check_img_alt(check_site_dict, list_page_status_code_200, list_empty_title):
    list_result = []
    for page in list_page_status_code_200:

        if page not in list_empty_title:
            title = check_site_dict["page_list"][page]["page_content"]["title"]

            try:
                amount_img = check_site_dict["page_list"][page]["page_content"]["images_alt"]["img_amount"]
                list_alt = check_site_dict["page_list"][page]["page_content"]["images_alt"]["list_atl"]
                flag = False
                for alt in list_alt:
                    if len(list_alt) != amount_img or alt != title:
                        flag = True
                if flag:
                    list_result.append(page)
            except:
                pass
    return list_result


def check_satus_cod_200(check_site_dict, list_page_status_code_200):
    dict_result = {}
    external_link = []
    for page in list_page_status_code_200:
        external_link += check_site_dict["page_list"][page]["page_content"]["external_link"]
    for page in set(external_link):
        status_cod = get_url_status_cod(page)
        if status_cod != 200:
            dict_result[page] = status_cod
    return dict_result


# get a dictionary with the parsed data
def get_result_dict(google_dict, check_site_dict):
    page_count_comparison = check_amount(google_dict, check_site_dict)
    list_page_status_code_200 = list(
        filter(lambda x: check_site_dict["page_list"][x]["status_code"] == 200, check_site_dict["page_list"]))
    list_comparison_title = comparison_len_title_or_descriptions(google_dict, check_site_dict,
                                                                 list_page_status_code_200, "title")
    list_comparison_description = comparison_len_title_or_descriptions(google_dict, check_site_dict,
                                                                       list_page_status_code_200, "description")
    list_empty_title = check_empty_title_or_description(check_site_dict, list_page_status_code_200, "title")
    list_empty_description = check_empty_title_or_description(check_site_dict, list_page_status_code_200, "description")
    list_h1 = check_h1(check_site_dict, list_page_status_code_200)
    list_page_canonical_missing = check_missing_canonical(check_site_dict, list_page_status_code_200)
    page_status = check_page_status(check_site_dict)
    list_wrong_h_structure = check_h_tag_structure(check_site_dict, list_page_status_code_200)
    list_wrong_img = check_img_alt(check_site_dict, list_page_status_code_200, list_empty_title)
    list_external_link = check_satus_cod_200(check_site_dict, list_page_status_code_200)

    result_analysis = {
        "check_robots": check_site_dict["robots"],
        "page_count_comparison": page_count_comparison,
        "list_comparison_title": list_comparison_title,
        "list_comparison_description": list_comparison_description,
        "list_empty_title": list_empty_title,
        "list_empty_description": list_empty_description,
        "list_h1_not_alone": list_h1,
        "list_page_canonical_missing": list_page_canonical_missing,
        "page_status": page_status,
        "list_wrong_h_structure": list_wrong_h_structure,
        "list_wrong_img": list_wrong_img,
        "list_external_link": list_external_link
    }
    return result_analysis


def main():
    google_dict = JsonRW().json_read("google_result")
    check_site_dict = JsonRW().json_read("check_result")
    result_analysis = get_result_dict(google_dict, check_site_dict)
    JsonRW().json_write("result_analysis", result_analysis)


if __name__ == "__main__":
    main()
