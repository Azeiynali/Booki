// {% raw %}
Vue.component("post", {
    props: {
        id: {},
        comment_length: {},
        content: {},
        username: {},
        img: {},
        image: {},
        avatar: {},
        date: "",
        like_classes: {
            default: ""
        },
        likes: {
            default: 0,
        },
        iw: {
            default: false,
        },
        classes: { default: "post" },
        comment_show: { default: true },
    },
    data() {
        return {
            is: true,
            delete_button: "حذف"
        };
    },

    methods: {
        like() {
            // this function to like the post
            // if not liked
            if (this.like_classes) {
                var data = new FormData();
                data.append('postId', this.id)
                fetch('/api/unlike', {
                    method: "POST",
                    body: data,
                }).then((response) => { return response.json() }).then(
                    (data) => {
                        if (data.success) {
                            this.$refs.like_icon.style.color = "black"
                            this.like_classes = "";
                            this.likes--;
                        }
                    })
            // if liked
            } else {
                var data = new FormData();
                data.append('postId', this.id)
                fetch('/api/like', {
                    method: "POST",
                    body: data,
                }).then((response) => { return response.json() }).then(
                    (data) => {
                        if (data.success) {
                            this.$refs.like_icon.style.color = "var(--red)"
                            this.like_classes = "liked";
                            this.likes++;
                        }
                    })
            }
        },
        delete_() {
            // this function to delete the post
            if (
                this.$refs.itrash.getAttribute("class") ===
                "fi fi-rr-check"
            ) {
                var myHeaders = new Headers();
                myHeaders.append(
                    "Content-Type",
                    "application/x-www-form-urlencoded"
                );

                var urlencoded = new URLSearchParams();
                urlencoded.append("id", this.id);
                var requestOptions = {
                    method: "DELETE",
                    headers: myHeaders,
                    body: urlencoded,
                    redirect: "follow",
                };

                fetch("/api/delete", requestOptions)
                    .then((response) => response.text())

                    .then((result) => {
                        this.is = false;
                    })
                    .catch((error) => console.log("error", error));
            } else {
                this.$refs.itrash.setAttribute(
                    "class",
                    "fi fi-rr-check"
                );
                this.$refs.trash.setAttribute("class", "px-3 gap-10 py-2 rounded flex items-center border-2 border-[#6d6d6d] transition-all duration-300 ease-out hover:opacity-90 bg-white flex-none cursor-pointer justify-center liked");
                this.delete_button = "مطمئنید؟"
            }
        },
    },
    template: `
                    <div v-if="is" :class="classes">
                        <div dir="rtl" class="flex justify-start text-lg w-9/10 text-[#292929] gap-2 relative h-20 user items-center mr-5">
                            <a :href="'\@' + username">
                                <img :src="avatar" />
                            </a>
                            <a :href="'\@' + username">
                                <div>
                                    <p>
                                        {{ username }}

                                    </p>
                                    <small>{{ date }}</small>
                                </div>
                            </a>
                        </div>
                        <div dir="rtl" class="flex gap-3 items-center justofy-center flex-col">
                            <img @dblclick="like" v-if="image != 'http://127.0.0.1:5000/static/pictures/select_post_image.png'" class="img" :src="image" />
                            <p class="text-start" v-html="content"></p>
                        </div>
                        <div dir="rtl" class="flex flex-none flex-wrap flex-row gap-3 mt-16 border-t-2 border-[#2929292f] pt-3">
                            <div @click="like" ref="like" :class="'px-3 gap-10 py-2 rounded flex items-center justify-between border-2 border-[#6d6d6d] transition-all duration-300 ease-out hover:opacity-90 cursor-pointer  bg-white flex-none ' + like_classes">
                                <i ref="like_icon" class="fi fi-rr-circle-heart"></i>
                                <small>{{ likes }}</small>
                            </div>
                            <div v-if="comment_show" @click="window.location.href = '/post/' + id" class="px-3 gap-10 py-2 rounded flex items-center transition-all duration-300 ease-out hover:opacity-90 bg-white flex-none justify-between border-2 border-[#005be4] text-[#005be4] cursor-pointer  text-[#6969ff]">
                                <i class="fi fi-rr-comment"></i>
                                <small>{{ comment_length }}</small>
                            </div>
                            <div v-if="iw" @click="delete_" ref="trash" class="px-3 gap-10 py-2 rounded flex items-center border-2 border-[#6d6d6d] transition-all duration-300 ease-out hover:opacity-90 bg-white flex-none cursor-pointer justify-center">
                                {{ delete_button }} <i ref="itrash" class="fi fi-rr-trash-xmark"></i>
                            </div>
                            </a>
                        </div>
                    </div>
                `
});
// {% endraw %}