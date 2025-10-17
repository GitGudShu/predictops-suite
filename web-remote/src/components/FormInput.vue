<template>
    <div class="form-group">
        <div class="values">
            <div class="prefix-div form-control" :style="{ backgroundColor: bgColor, color: txtColor }">{{ displayPrefix }}
            </div>
            <input class="form-control" :style="{ backgroundColor: bgColor, color: txtColor }" :value="value"
                :disabled="disabled" type="number" @input="updateValue" />
        </div>
        <div class="operators" v-if="yellow && operatorValue !== '0'">
            <q-icon name="fa-solid fa-arrow-turn-up" class="rotate-90" style="color: var(--sad-nightblue);" size="xs"/>
            <div class="prefix-div form-control" :style="{ backgroundColor: bgColor, color: txtColor }">{{
                operatorDisplayPrefix }}</div>
            <input class="form-control" :style="{ backgroundColor: bgColor, color: txtColor }" :value="operatorValue"
                :disabled="disabled" type="number" @input="updateOperatorValue" />
                <span class="suffix-operators form-control" :style="{ backgroundColor: bgColor, color: txtColor }" @click="focusOnInput">opérateurs</span>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
    prefix: String,
    operatorPrefix: String,
    value: [String, Number],
    operatorValue: [String, Number],
    yellow: Boolean,
    bgColor: String,
    txtColor: String,
    disabled: Boolean
});

const emit = defineEmits(['update:modelValue', 'update:operatorValue']);

const displayPrefix = computed(() => {
    if (props.prefix) {
        return props.prefix + " ";
    }
    return "";
});

const operatorDisplayPrefix = computed(() => {
    if (props.operatorPrefix) {
        return props.operatorPrefix + " ";
    }
    return "";
});

const updateValue = (event) => {
    emit('update:modelValue', event.target.value);
}

const updateOperatorValue = event => {
    emit('update:operatorValue', event.target.value);
};

const focusOnInput = (event) => {
    const input = event.target.previousSibling
    input.focus()
}
</script>

<style scoped>

.values, .operators {
    flex: 1 0 auto;
    display: flex;
    align-items: center;
    /* justify-content: ce; */
    padding: 0.5rem;
}

.values input {
    border-radius: 0 0.25rem 0.25rem 0 !important;
}

.operators input {
    width: clamp(2ch, 3ch, 4ch);
    min-width: 2ch;
    max-width: 4ch;
}
.operators i {
    padding: 0.125em;
}

.operators .suffix-operators {
    border-radius: 0 0.25rem 0.25rem 0 !important;
    width: fit-content;
    font-size: clamp(10px, 1vw, 14px);
    line-height: 1.5rem;
    padding-right: 5px !important ;
}

.form-group {
    flex: 1 0 auto;
    display: flex;
    flex-direction: column;
    justify-content: center;
    width: min-content;
    max-width: 100%;
}

.bounds-form .prefix-div {
    white-space: nowrap;
    width: max-content;
    border: none;
    border-radius: 0.25rem 0 0 0.25rem !important;
    padding: 0.375rem 0rem 0.375rem 0.25rem;
    font-weight: bold;
}

.bounds-form .form-control {
    border-radius: 0;
    padding: 0.375rem 0em 0.375rem 0.25rem;
}

.form-control {
    width: 100%;
    padding: .375rem .75rem;
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.5;
    color: #212529;
    background-color: #fff;
    background-clip: padding-box;
    border: 1px solid #ced4da;
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    border-radius: .25rem;
    transition: border-color .15s ease-in-out, box-shadow .15s ease-in-out;
}

/* Chrome, Safari, Edge, Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}

/* Firefox */
input[type=number] {
    -moz-appearance: textfield;
    appearance: textfield;
}


.bounds-form input,
span {
    border: none !important;
}

.form-control:focus {
    box-shadow: none;
    outline: none;
}

.disabled, [disabled] {
    opacity: 1 !important;
}

</style>
