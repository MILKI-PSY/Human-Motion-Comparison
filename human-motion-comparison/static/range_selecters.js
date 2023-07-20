function update_marks_info(e) {
    let columns = $(e.currentTarget).find("th");
    let ranges = [], total = 0, i, w;
    for (i = 0; i < columns.length; i++) {
        w = columns.eq(i).width() + 3; // 2 for paddings and 1 for border
        ranges.push(w);
        total += w;
    }

    let curser = 0;
    let frame_number = 0;
    let marks_inputs = $('#marks').find('input');

    for (let i = 0; i < ranges.length - 1; i++) {
        curser += ranges[i];
        frame_number = Math.round((curser / total) * (end_reference - start_reference) + start_reference);
        marks_inputs.eq(i).val(frame_number);
        marks[i] = frame_number;
    }
}

function update_selected_range_info(e) {
    let columns = $(e.currentTarget).find("th");
    let ranges = [], i, w;
    for (i = 0; i < columns.length; i++) {
        w = columns.eq(i).width() + 3; // 2 for padding and 1 for border
        console.log(w);
        ranges.push(w);
    }
    let total = $('.frames_selector_div').width();
    console.log(total);
    let temp_percent = Math.round(ranges[0] / total * 100) / 100;
    selected_range[0] = Math.round(temp_percent * (end_recording - start_recording) + start_recording);
    temp_percent = Math.round((ranges[0] + ranges[1]) / total * 100) / 100;
    selected_range[1] = Math.round(temp_percent * (end_recording - start_recording) + start_recording)
    console.log(selected_range[1]);
    $('#range_start').val(selected_range[0]);
    $('#range_end').val(selected_range[1]);
}

function set_reference_range() {
    $('#reference_start_p').text(start_reference);
    $('#reference_end_p').text(end_reference);
}

function set_recording_range() {
    $('#recording_start_p').text(start_recording);
    $('#recording_end_p').text(end_recording);
}

function set_marks() {
    let marks_div = $('#marks');
    let marks_inputs = marks_div.find('input');
    let difference_value = Math.abs(marks_inputs.length - marks.length);
    $(".weights_setter").colResizable({disable: true});
    if (marks_inputs.length <= marks.length) {
        for (let i = 0; i < difference_value; i++) {
            $('.weights-setter-tr').prepend('<th class="range weights_th"></th>')

            marks_div.append(
                '<div class="col col-md-6 md-3">\n' +
                '   <div class="input-group">\n' +
                '       <input type="number" class="form-control">\n' +
                '       <div class="input-group-prepend">\n' +
                '           <button class="input-group-btn btn btn-danger sub-mark">-</button>\n' +
                '       </div>\n' +
                '   </div>\n' +
                '</div>'
            );
        }
    } else {
        for (let i = difference_value - 1; i >= 0; i--) {
            $('.weights-setter-tr').find('th').eq(i).remove();
            $("#marks").find('.col').eq(i).remove();
        }
    }

    let weights_setter_div = $('.weights_setter_div');
    let ths = weights_setter_div.find('th');
    let marks_with_start = [...marks];
    let percentage, new_width;
    marks_with_start.unshift(start_reference);
    marks_with_start.push(end_reference);

    for (let i = 0; i < marks_with_start.length - 1; i++) {
        ths.eq(i).data('index', i);
        percentage = (marks_with_start[i + 1] - marks_with_start[i]) / (end_reference - start_reference);
        new_width = Math.round(percentage * weights_setter_div.width() - 3); //2 for padding, 1 for border
        ths.eq(i).width(new_width + 'px');
    }

    setTimeout(function () {
        $(".weights_setter").colResizable({
            liveDrag: true,
            draggingClass: "rangeDrag",
            onResize: update_marks_info,
            minWidth: 3
        });
    }, 100);

    for (let i = 0; i < marks.length; i++) {
        marks_div.find('input').eq(i).val(marks[i]);
    }
    marks_div.find('input').each(function (i) {
        $(this).data('index', i);
    });
    marks_div.find('button').each(function (i) {
        $(this).data('index', i);
    });
}

function set_frames_ranges() {
    let frames_selector_div = $('.frames_selector_div');
    let ths = frames_selector_div.find('th');
    let all_marks = [...selected_range];
    all_marks.unshift(start_recording);
    all_marks.push(end_recording);
    let percentage, new_width, all_width = 0;

    ($(".frames_selector").colResizable({disable: true}))


    for (let i = 0; i < all_marks.length - 1; i++) {
        percentage = (all_marks[i + 1] - all_marks[i]) / (end_recording - start_recording);
        new_width = Math.round(percentage * frames_selector_div.width() - 3); //2 for padding, 1 for border
        all_width += new_width;
        ths.eq(i).css({width: new_width + "px"});
    }

    setTimeout(function () {
        $(".frames_selector").colResizable({
            liveDrag: true,
            draggingClass: "rangeDrag",
            onResize: update_selected_range_info,
            minWidth: 3
        });
    }, 100);

    $('#range_start').val(selected_range[0]);
    $('#range_end').val(selected_range[1]);
}

function set_references_list(reference_names) {
    $(".references_btn").each(function (index) {
        let value = $(this).val();
        let index_to_remove = reference_names.indexOf(value);
        console.log(index_to_remove);
        if (index_to_remove === -1) {
            $(this).parent().parent().remove();
        } else {
            reference_names.splice(index_to_remove, 1);
        }
    });

    for (let i in reference_names) {
        $("#reference-list").prepend(
            '<div  class="row mt-3">\n' +
            '    <div class="col col-md-12 btn-group">\n' +
            '       <button class="input-group-btn form-control references_btn" value="' + reference_names[i] + '">' + reference_names[i] + '</button>\n' +
            '       <button class="input-group-btn btn btn-danger del-reference" value="' + reference_names[i] + '">-</button>\n' +
            '    </div>\n' +
            '</div>\n'
        );
    }
}

function set_recordings_list(recording_name) {
    let recording_list = $("#recording-list")
    recording_list.empty();
    for (let i in recording_name) {
        recording_list.prepend(
            '<div  class="row mt-3">\n' +
            '    <div class="col col-md-12 btn-group">\n' +
            '       <button class="input-group-btn form-control recording_btn" value="' + recording_name[i] + '">' + recording_name[i] + '</button>\n' +
            '       <button class="input-group-btn btn btn-danger del-recording" value="' + recording_name[i] + '">-</button>\n' +
            '    </div>\n' +
            '</div>\n'
        );
    }
}

function set_source_list(recording_names) {
    let source_list = $("#recording_name")
    source_list.empty();
    for (let i in recording_names) {
        source_list.append("<option value=" + recording_names[i] + ">" + recording_names[i] + "</option>");
    }
}